from datetime import datetime

html_content = f"""
<html>
<head>
    <title>F1 Test Page</title>
</head>
<body style="font-family: Arial; background:#111; color:#0f0;">
    <h1>🚀 Bot is Working</h1>
    <p>Updated at: {datetime.utcnow()} UTC</p>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html_content)

print("index.html updated successfully")
