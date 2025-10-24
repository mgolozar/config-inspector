import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from config_validator.cli import main

if __name__ == "__main__":
    raise SystemExit(main())