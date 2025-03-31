import pandas as pd
import matplotlib.pyplot as plt
import sys
from collections import defaultdict
from matplotlib.ticker import ScalarFormatter
import matplotlib.font_manager as fm

import matplotlib.pyplot as plt


ft = defaultdict(int)

# Count the frequency of each character

for c in sys.stdin.read():
    ft[c.lower()] += 1

# replace keys
ft['SP'] = ft.pop(chr(0x20))
ft['CR'] = ft.pop(chr(0x0d))
ft['LF'] = ft.pop(chr(0x0a))
ft['00'] = ft.pop('␀')

# Sort the dictionary by value
ft = dict(sorted(ft.items(), key=lambda x: x[1], reverse=True))

keys = list(ft.keys())[:60]
values = list(ft.values())[:60]

fig, ax = plt.subplots(figsize=(5, 5))  # Set figure size to be square

# Create bar chart
ax.bar(keys, values, color='blue')

# Ensure the plotting area is square
ax.set_box_aspect(1) 

# Remove horizontal margins
ax.margins(x=0)

# Disable scientific notation on y-axis
ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
ax.ticklabel_format(style='plain', axis='y')

# Reduce font size of x-axis labels
ax.set_xticklabels(keys, fontsize=8)  # Adjust fontsize as needed

# Labels and title
ax.set_xlabel("Character")
ax.set_ylabel("Count")
ax.set_title("Character Frequencies In 70000 Sent And Received E-mails From My Mailbox")


# Show plot
plt.show()
