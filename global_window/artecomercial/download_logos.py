import urllib.request
import os

dest_dir = r"C:\Users\pietr\OneDrive\.vscode\global_window\artecomercial\public\images\marcas"
os.makedirs(dest_dir, exist_ok=True)

# Using high quality transparent SVGs or PNGs
logos = {
    "tama": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Tama_Drums_logo.svg",
    "pearl": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Pearl_Drums_logo.svg",
    "yamaha": "https://upload.wikimedia.org/wikipedia/commons/4/41/Yamaha_logo.svg", # Yamaha standard
    "daddario": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/D%27Addario_logo.png/1200px-D%27Addario_logo.png",
    "vandoren": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Vandoren_logo.svg/1024px-Vandoren_logo.svg.png",
    "evans": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d1/Evans_Drumheads_logo.png/640px-Evans_Drumheads_logo.png"
}

for name, url in logos.items():
    ext = ".svg" if url.endswith(".svg") else ".png"
    dest = os.path.join(dest_dir, f"{name}{ext}")
    # adding headers to avoid 403 Forbidden
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Downloaded {name}{ext}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
