import heapq
import sys
from collections import defaultdict

# Helper function to build the Huffman tree and generate the codes
def build_huffman_tree(text):
    # Calculate the frequency of each symbol in the text
    frequency = defaultdict(int)
    for symbol in text:
        frequency[symbol] += 1

    print(frequency)

    # Build a priority queue (min-heap) with symbols and their frequencies
    heap = [[weight, [symbol, ""]] for symbol, weight in frequency.items()]
    heapq.heapify(heap)

    # Build the Huffman tree
    while len(heap) > 1:
        low = heapq.heappop(heap)
        high = heapq.heappop(heap)
        for pair in low[1:]:
            pair[1] = '0' + pair[1]
        for pair in high[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [low[0] + high[0]] + low[1:] + high[1:])

    # Extract the final codes from the heap
    huffman_tree = heap[0]
    huffman_codes = {symbol: code for symbol, code in huffman_tree[1:]}

    return huffman_codes

# Example usage:
def huffman_code_table(text):
    return build_huffman_tree(text)

# Example input text
code_table = huffman_code_table(sys.stdin.read())

# Output the Huffman code table
print("Huffman Code Table:")
print(code_table)
