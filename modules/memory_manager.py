"""
Memory management module for storing conversation history.
Includes cleanup functionality to prevent unbounded growth.
"""
import json
import os
from pathlib import Path
from utils.config import MAX_MEMORY_ENTRIES

# Get current file's directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MEM_FILE = DATA_DIR / "memory.json"

# Ensure the data directory exists
DATA_DIR.mkdir(exist_ok=True)

def save_memory(user_input: str, ai_response: str):
    """
    Save a conversation pair to memory.
    
    Args:
        user_input: User's input text
        ai_response: AI's response text
    """
    try:
        # Ensure directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save as JSONL (one JSON object per line)
        with open(MEM_FILE, "a", encoding="utf-8") as f:
            json.dump({"user": user_input, "ai": ai_response}, f, ensure_ascii=False)
            f.write("\n")
        
        # Periodically clean up if file gets too large
        if os.path.getsize(MEM_FILE) > MAX_MEMORY_ENTRIES * 200:  # Rough estimate
            cleanup_memory()
            
    except Exception as e:
        print(f"⚠️ Warning: Could not save memory: {e}")

def load_memory(limit=None):
    """
    Load conversation memory from file.
    
    Args:
        limit: Maximum number of entries to load (None for all)
        
    Returns:
        list: List of conversation dictionaries
    """
    if not MEM_FILE.exists():
        return []
    
    try:
        memories = []
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        memories.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines
        
        # Return most recent entries if limit specified
        if limit and len(memories) > limit:
            return memories[-limit:]
        
        return memories
    except Exception as e:
        print(f"⚠️ Warning: Could not load memory: {e}")
        return []

def cleanup_memory(keep_last=500):
    """
    Clean up memory file by keeping only the most recent entries.
    
    Args:
        keep_last: Number of recent entries to keep
    """
    try:
        memories = load_memory()
        if len(memories) <= keep_last:
            return  # No cleanup needed
        
        # Keep only the most recent entries
        memories_to_keep = memories[-keep_last:]
        
        # Backup old file
        backup_file = MEM_FILE.with_suffix('.json.bak')
        if MEM_FILE.exists():
            import shutil
            shutil.copy2(MEM_FILE, backup_file)
        
        # Write back only recent entries
        with open(MEM_FILE, "w", encoding="utf-8") as f:
            for memory in memories_to_keep:
                json.dump(memory, f, ensure_ascii=False)
                f.write("\n")
        
        print(f"🧹 Cleaned up memory: kept {len(memories_to_keep)} most recent entries")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not cleanup memory: {e}")

def clear_memory():
    """Clear all memory (use with caution)."""
    try:
        if MEM_FILE.exists():
            backup_file = MEM_FILE.with_suffix('.json.bak')
            import shutil
            shutil.copy2(MEM_FILE, backup_file)
            MEM_FILE.unlink()
            print("🗑️ Memory cleared (backup saved)")
    except Exception as e:
        print(f"⚠️ Warning: Could not clear memory: {e}")
