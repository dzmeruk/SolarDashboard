# Allows tests located in "tests" subdirectory to import modules in "scripts"######################
import sys
from pathlib import Path

def path_to_scripts():
    BASE_DIR = Path(__file__).resolve().parent.parent # defines BASE_DIR as the directory above tests
    sys.path.append(str(BASE_DIR/"scripts"))
