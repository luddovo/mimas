class Bitstream:
    encoding_map = {'T': '0000', 'Z': '000100', '!': '000101000', 'Q': '000101001', '7': '00010101', '5': '00010110', '%': '0001011100', '?': '0001011101', '<': '000101111', '␀': '000110', 'G': '000111', '2': '0010000', '/': '0010001', 'Y': '001001', '\n': '00101', 'M': '00110', '-': '00111', ' ': '010', '4': '01100000', '>': '01100001', ',': '0110001', 'W': '0110010', '0': '0110011', 'U': '01101', 'O': '0111', 'A': '1000', 'D': '10010', 'L': '10011', ')': '10100000', "'": '10100001', '1': '1010001', 'J': '1010010', '=': '1010011', 'K': '101010', '3': '10101100', '6': '101011010', '+': '101011011', '8': '101011100', 'X': '101011101', '(': '101011110', '9': '101011111', 'C': '10110', 'S': '10111', 'P': '110000', 'F': '1100010', ':': '1100011', 'V': '110010', '.': '110011', 'E': '1101', 'R': '11100', '*': '1110100', 'B': '1110101', 'H': '111011', 'I': '11110', 'N': '11111'}

    def __init__(self, byte_stream=None):
        """Initialize the bitstream. If byte_stream is provided, start reading from it."""
        self.bits = 0
        self.bit_count = 0
        self.bytes_written = bytearray()
        
        if byte_stream:
            self.byte_stream = byte_stream  # Initialize with byte stream for reading
            self.read_position = 0  # Pointer to track the position in the byte stream
        else:
            self.byte_stream = None
            self.read_position = None

    def append(self, bitstring):
        """Append a binary string (bitstring) to the bitstream."""
        for bit in bitstring:
            self.bits = (self.bits << 1) | int(bit)  # Shift left and append the bit
            self.bit_count += 1
        
        # If we have accumulated 8 bits, write to bytes_written
        while self.bit_count >= 8:
            byte = (self.bits >> (self.bit_count - 8)) & 0xFF  # Extract the top 8 bits
            self.bytes_written.append(byte)  # Store this byte
            self.bit_count -= 8  # Decrease the bit count

    def write_fixed_width(self, token, num_bits):
        """Write a fixed-width token to the bitstream."""
        bit_string = format(token, f'0{num_bits}b')  # Convert token to binary with leading zeros
        self.append(bit_string)

    def write_huffman(self, token):
        """Write a Huffman-encoded token to the bitstream."""
        if token not in self.encoding_map:
            raise ValueError(f"Token '{token}' is not in the encoding map.")
        huffman_code = self.encoding_map[token]  # Get the Huffman code for the token
        self.append(huffman_code)

    def write_huffman_string(self, string):
        for c in string+'␀': self.write_huffman(c)

    def read_fixed_width(self, num_bits):
        """Read a specific number of bits from the byte stream."""
        bit_string = ''
        bits_read = 0
        byte_index = self.read_position // 8
        bit_offset = self.read_position % 8
        
        while bits_read < num_bits:
            byte = self.byte_stream[byte_index]
            bits_left_in_byte = 8 - bit_offset
            bits_to_read = min(bits_left_in_byte, num_bits - bits_read)
            
            # Extract bits from the current byte
            shift = bits_left_in_byte - bits_to_read
            bit_string += format((byte >> shift) & ((1 << bits_to_read) - 1), f'0{bits_to_read}b')
            
            # Update bit and byte pointers
            bits_read += bits_to_read
            bit_offset += bits_to_read
            if bit_offset == 8:
                byte_index += 1
                bit_offset = 0
        
            self.read_position = byte_index * 8 + bit_offset
        
        return int(bit_string, 2)

    def read_huffman(self):
        """Read a Huffman-encoded token from the byte stream."""
        reverse_map = {v: k for k, v in self.encoding_map.items()}
        current_bits = ''
        byte_index = self.read_position // 8
        bit_offset = self.read_position % 8
        
        while byte_index < len(self.byte_stream):
            byte = self.byte_stream[byte_index]
            bit = (byte >> (7 - bit_offset)) & 1
            current_bits += str(bit)
            bit_offset += 1
            self.read_position += 1
            
            if current_bits in reverse_map:
                return reverse_map[current_bits]
            
            # If we've consumed all bits in the current byte, move to the next byte
            if bit_offset == 8:
                byte_index += 1
                bit_offset = 0
        
        raise IndexError("No valid Huffman code found at current position.")

    def read_huffman_string(self):
        s =''
        c = self.read_huffman()
        while c != '␀':
            s += c
            c = self.read_huffman()
        return s

    def export(self):
        """Export the written bits as bytes."""
        if self.bit_count > 0:  # If there are leftover bits that haven't been written
            byte = (self.bits << (8 - self.bit_count)) & 0xFF  # Pad the bits and extract the byte
            self.bytes_written.append(byte)

        return bytes(self.bytes_written)  # Return the final bitstream as bytes

    def length(self):
        """Get the current length of the bitstream in bits."""
        return self.bit_count

    def remaining(self):
        """Get the number of remaining bits in the bitstream."""
        return len(self.bytes_written) * 8 - self.bit_count

