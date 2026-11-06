with open(r'C:\Users\tiruv\Desktop\milestone2\Backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()
import re
matches = re.finditer(r'@apple\.(get)\("/.*?sub.*?"', content)
for m in matches:
    print(m.group(0))
