import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/filter_million_reels.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Run the extraction and print each candidate in full detail
import subprocess
result = subprocess.run(['python', 'scratch/filter_million_reels.py'], capture_output=True, text=True, encoding='utf-8')
print(result.stdout)
