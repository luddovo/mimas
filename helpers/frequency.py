import sys
from collections import defaultdict

ft = defaultdict(int)

for c in sys.stdin.read():
    ft[c.lower()] += 1

ft = dict(sorted(ft.items(), key=lambda x: x[1], reverse=True))

print("character, code, count")
for key in ft:
    print(f"{key},{ord(key)},{ft[key]}")
