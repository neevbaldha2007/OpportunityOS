import sys
from pathlib import Path

# Support importing load_skills_from_csv from either seeds or app.seeds
try:
    from seeds.load_skills import load_skills_from_csv, find_skills_csv
except ImportError:
    backend_dir = Path(__file__).resolve().parent.parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    from seeds.load_skills import load_skills_from_csv, find_skills_csv

__all__ = ["load_skills_from_csv", "find_skills_csv"]
