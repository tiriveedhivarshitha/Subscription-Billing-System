import io
import re

with io.open(r"C:\Users\tiruv\Desktop\milestone2\Backend\main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Let's find all the @apple.post related to subscriptions
matches = re.finditer(r'@apple\.(post|put)\("/subscriptions/[^"]+"', content)
for m in matches:
    print(m.group(0))
