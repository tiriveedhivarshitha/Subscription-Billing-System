with open(r'C:\Users\tiruv\Desktop\milestone2\Backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()
import re
for m in re.finditer(r'@apple\.(get)\("[^"]+"', content):
    print(m.group(0))
