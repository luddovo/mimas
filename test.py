import base91, bitstream
import sys

bs = bitstream.Bitstream()
data = sys.stdin.read()
cnt = 0
l = len(data)
for c in data:
    cnt += 1
    if cnt % 10000 == 0:
        sys.stderr.write(f"Processing: {cnt/l}%\n")
    bs.write_huffman(c)
print(len(bs.bytes_written))
encoded_data = base91.encode(bs.export())
print(encoded_data)