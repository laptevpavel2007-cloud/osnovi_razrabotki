import shutil
import os
import glob

def safe_remove_dir(path):
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)

def safe_remove_file(path):
    if os.path.exists(path) and os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass

if __name__ == '__main__':
    for d in ['.venv', 'venv', 'build', 'dist']:
        safe_remove_dir(d)
    
    for pattern in ['**/__pycache__', '**/.mypy_cache', '**/.ruff_cache', '**/.pytest_cache', '**/*.egg-info']:
        for d in glob.glob(pattern, recursive=True):
            safe_remove_dir(d)
            
    for f in glob.glob('**/*.pyc', recursive=True):
        safe_remove_file(f)
        
    print("Cleaning completed.")