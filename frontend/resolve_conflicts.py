import io, re

with io.open(r"C:\Users\tiruv\Desktop\milestone2\frontend\dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

# Strategy: keep only content between "=======" and end (the newer/better version)
# The pattern: <<<<<<< HEAD ... ======= GOOD_CONTENT >>>>>>> (or end)
# We keep the SECOND part of each conflict (after =======)

def resolve_conflicts_keep_theirs(text):
    result = []
    lines = text.splitlines(keepends=True)
    in_conflict = False
    in_ours = False  # between <<<< and ====
    in_theirs = False  # between ==== and >>>>

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<<<<<<<'):
            in_conflict = True
            in_ours = True
            in_theirs = False
            continue
        elif stripped == '=======' and in_conflict:
            in_ours = False
            in_theirs = True
            continue
        elif stripped.startswith('>>>>>>>') and in_conflict:
            in_conflict = False
            in_ours = False
            in_theirs = False
            continue

        if not in_conflict:
            result.append(line)
        elif in_theirs:
            result.append(line)

    return ''.join(result)

fixed = resolve_conflicts_keep_theirs(content)

with io.open(r"C:\Users\tiruv\Desktop\milestone2\frontend\dashboard.html", "w", encoding="utf-8") as f:
    f.write(fixed)
print("Conflict markers resolved. Lines kept:", len(fixed.splitlines()))
