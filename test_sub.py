import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from importlib import import_module

base_path = "app/webhooks/out"
for root, dirs, files in os.walk(base_path):
    if "subscriber.py" in files:
        rel_path = os.path.relpath(root, os.getcwd())
        normalized_root = rel_path.replace("\\", "/").replace("/", ".")
        module_path = f"{normalized_root}.subscriber"
        print(f"Computed module path: {module_path}")
        try:
            import_module(module_path)
            print(f"Successfully imported {module_path}")
        except Exception as e:
            print(f"Failed to import {module_path}: {e}")
