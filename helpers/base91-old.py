# Base91 encoding/decoding implementation
class Base91:
    def __init__(self):
        self._alphabet = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~"'
        self._base = 91
        self._lookup = {ch: i for i, ch in enumerate(self._alphabet)}

    def encode(self, data: bytes) -> str:
        """Encode bytes to Base91 string"""
        if not data:
            return ""
        
        result = bytearray()
        v = 0
        bits = 0
        
        for byte in data:
            v |= byte << bits
            bits += 8
            while bits >= 13:
                bits -= 13
                result.extend(self._alphabet[v & 8191:][:1])
                v >>= 13
                if v > 90:
                    bits -= 1
        
        if bits:
            result.extend(self._alphabet[v & 8191:][:1])
            if bits > 7 or v > 90:
                result.extend(self._alphabet[v >> bits:][:1])
                
        return result.decode('ascii')

    def decode(self, data: str) -> bytes:
        """Decode Base91 string to bytes"""
        if not data:
            return b""
        
        data = data.encode('ascii')
        result = bytearray()
        v = -1
        bits = 0
        
        for ch in data:
            if ch not in self._lookup:
                continue
                
            if v < 0:
                v = self._lookup[ch]
            else:
                v += self._lookup[ch] * 91
                bits += 13
                while bits >= 8:
                    bits -= 8
                    result.append(v >> bits & 255)
                v &= (1 << bits) - 1
                
        if v >= 0 and bits > 0:
            result.append(v << (8 - bits) & 255)
            
        return bytes(result)

# Example usage
def main():
    base91 = Base91()
    
    # Test encoding
    original = b"Hello, World!"
    encoded = base91.encode(original)
    print(f"Original: {original}")
    print(f"Encoded: {encoded}")
    
    # Test decoding
    decoded = base91.decode(encoded)
    print(f"Decoded: {decoded}")
    
    # Verify
    print(f"Match: {original == decoded}")

if __name__ == "__main__":
    main()