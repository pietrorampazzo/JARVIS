import os
import glob
import shutil

src_dir = r"C:\Users\pietr\Downloads"
dest_dir = r"C:\Users\pietr\OneDrive\.vscode\global_window\artecomercial\public\images\marcas"

os.makedirs(dest_dir, exist_ok=True)

keywords = ['pearl', 'tama', 'yamaha', 'daddario', 'vandoren', 'evans']

files = [f for f in glob.glob(os.path.join(src_dir, '*.*')) if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]

for kw in keywords:
    # Find newest file matching keyword
    matches = [f for f in files if kw in os.path.basename(f).lower()]
    if matches:
        matches.sort(key=os.path.getmtime, reverse=True)
        newest = matches[0]
        ext = os.path.splitext(newest)[1]
        dest_path = os.path.join(dest_dir, f"{kw}{ext}")
        shutil.copy2(newest, dest_path)
        print(f"Copied {os.path.basename(newest)} to {dest_path}")
    else:
        print(f"No file found for {kw}")
