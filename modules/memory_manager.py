import json, os

# Get current file's directory (e.g., /home/deepak/Desktop/Project/jarvis-v2/modules)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create data directory path relative to current file
DATA_DIR = os.path.join(BASE_DIR, "../data")
MEM_FILE = os.path.join(DATA_DIR, "memory.json")

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def save_memory(user, ai):
    print(f"📁 Saving memory to: {MEM_FILE}")
    with open(MEM_FILE, "a") as f:
        json.dump({"user": user, "ai": ai}, f)
        f.write("\n")

def load_memory():
    if os.path.exists(MEM_FILE):
        with open(MEM_FILE, "r") as f:
            return [json.loads(line) for line in f.readlines()]
    return []
