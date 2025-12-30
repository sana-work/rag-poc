import sys
import importlib

required_modules = [
    "fastapi", "uvicorn", "google.generativeai", 
    "sentence_transformers", "faiss", "sklearn", 
    "docx", "pypdf", "bs4", "dotenv"
]

print("Checking environment...")

missing = []
for mod in required_modules:
    try:
        importlib.import_module(mod)
        print(f"[OK] {mod}")
    except ImportError:
        # Some packages have different import names
        if mod == "sentence_transformers":
            try:
                import sentence_transformers
                print(f"[OK] {mod}")
            except:
                print(f"[MISSING] {mod}")
                missing.append(mod)
        elif mod == "docx":
            try:
                import docx
                print(f"[OK] {mod}")
            except:
                print(f"[MISSING] {mod}")
                missing.append(mod)
        elif mod == "bs4":
            try:
                import bs4
                print(f"[OK] {mod}")
            except:
                print(f"[MISSING] {mod}")
                missing.append(mod)
        elif mod == "dotenv":
            try:
                import dotenv
                print(f"[OK] {mod}")
            except:
                print(f"[MISSING] {mod}")
                missing.append(mod)
        elif mod == "google.generativeai":
            try:
                import google.generativeai
                print(f"[OK] {mod}")
            except:
                print(f"[MISSING] {mod}")
                missing.append(mod)
        else:
            print(f"[MISSING] {mod}")
            missing.append(mod)

if missing:
    print("\nWARNING: Some modules are missing. The app may run in reduced functionality mode.")
else:
    print("\nEnvironment looks good!")
