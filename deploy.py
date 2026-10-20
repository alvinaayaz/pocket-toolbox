import os
import subprocess

print("?? Starting Pocket Toolbox Build & Deploy Pipeline...")

# Step 1: Run build script
print("?? Compiling site via build.py...")
build_result = subprocess.run(["python", "build.py"])

if build_result.returncode != 0:
    print("? Build failed. Aborting deployment.")
    exit(1)

print("? Build complete! All assets compiled successfully.")
print("?? To deploy to GitHub Pages or static hosting, your output files are ready in the output directory.")

