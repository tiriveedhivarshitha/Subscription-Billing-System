import json
import os

frontend_dir = r"C:\Users\tiruv\Desktop\milestone2\frontend"

# 1. Create icon.svg
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
    <rect width="512" height="512" fill="#333333" rx="100"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="250" fill="white" font-family="Arial, sans-serif">$</text>
</svg>"""
with open(os.path.join(frontend_dir, "icon.svg"), "w") as f:
    f.write(svg_content)

# 2. Create manifest.json
manifest = {
    "name": "Subscription Billing Automation System",
    "short_name": "Billing App",
    "start_url": "index.html",
    "display": "standalone",
    "background_color": "#f4f4f4",
    "theme_color": "#333333",
    "icons": [
        {
            "src": "icon.svg",
            "sizes": "192x192 512x512 any",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }
    ]
}
with open(os.path.join(frontend_dir, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=4)

# 3. Create offline.html
offline_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline - Billing App</title>
    <link rel="stylesheet" href="style.css">
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f4f4f4; margin: 0; text-align: center; }
        .offline-card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 400px; }
        h1 { color: #333; }
        p { color: #666; margin-bottom: 20px; }
        .btn { padding: 10px 20px; background: #0056b3; color: white; border: none; cursor: pointer; border-radius: 4px; font-size: 16px; }
        .btn:hover { background: #004494; }
    </style>
</head>
<body>
    <div class="offline-card">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a15.16 15.16 0 0 1-1.58 2.19m-2.88 2.37A15.35 15.35 0 0 1 12 19c-7 0-10-7-10-7a15.42 15.42 0 0 1 4.54-5.32"></path><line x1="2" y1="2" x2="22" y2="22"></line></svg>
        <h1>You are Offline</h1>
        <p>An internet connection is required to securely access the billing system.</p>
        <button class="btn" onclick="window.location.reload()">Retry Connection</button>
    </div>
</body>
</html>"""
with open(os.path.join(frontend_dir, "offline.html"), "w") as f:
    f.write(offline_content)

print("Created icon, manifest, and offline.html")
