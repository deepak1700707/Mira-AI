"""
Utility module for managing runtime file paths.
Organizes all generated files into a structured runtime directory.
"""
from pathlib import Path
import os

# Base runtime directory
BASE_DIR = Path(__file__).parent.parent
RUNTIME_DIR = BASE_DIR / "runtime"

# Subdirectories for different file types
AUDIO_DIR = RUNTIME_DIR / "audio"
LOGS_DIR = RUNTIME_DIR / "logs"
TRANSCRIPTS_DIR = RUNTIME_DIR / "transcripts"

def ensure_runtime_dirs():
    """Create runtime directories if they don't exist."""
    for directory in [RUNTIME_DIR, AUDIO_DIR, LOGS_DIR, TRANSCRIPTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    return RUNTIME_DIR

def get_audio_path(filename="command.wav"):
    """Get path for audio file in runtime/audio/ directory."""
    ensure_runtime_dirs()
    return AUDIO_DIR / filename

def get_log_path(filename="mira_ai.log"):
    """Get path for log file in runtime/logs/ directory."""
    ensure_runtime_dirs()
    return LOGS_DIR / filename

def get_transcript_path(filename="output.txt"):
    """Get path for transcript file in runtime/transcripts/ directory."""
    ensure_runtime_dirs()
    return TRANSCRIPTS_DIR / filename

def cleanup_old_files(max_age_days=7):
    """
    Clean up old runtime files older than max_age_days.
    
    Args:
        max_age_days: Maximum age in days for files to keep
    """
    import time
    
    ensure_runtime_dirs()
    current_time = time.time()
    cutoff_time = current_time - (max_age_days * 24 * 60 * 60)
    
    cleaned_count = 0
    for directory in [AUDIO_DIR, TRANSCRIPTS_DIR]:
        if directory.exists():
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_time = file_path.stat().st_mtime
                    if file_time < cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                        except Exception:
                            pass
    
    if cleaned_count > 0:
        print(f"🧹 Cleaned up {cleaned_count} old runtime files (>{max_age_days} days)")

