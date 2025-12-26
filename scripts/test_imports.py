# Simple import test to detect syntax errors in modules
import importlib
import sys
from pathlib import Path

# Ensure project root is on sys.path (script runs from scripts/)
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

modules = [
    'tools.listings',
    'tools.cypher',
]

failed = False
for m in modules:
    try:
        importlib.import_module(m)
        print(f'OK: imported {m}')
    except Exception as e:
        print(f'ERROR importing {m}: {e}')
        failed = True

if failed:
    sys.exit(1)
else:
    print('All imports OK')
