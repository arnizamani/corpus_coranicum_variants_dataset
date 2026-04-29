import sys
from pathlib import Path

# Put the submodule's scripts/ directory on sys.path so tests can import
# `transliterate_to_arabic`, `normalize_arabic`, etc. without the
# `scripts.` prefix (these aren't packaged as a real Python module).
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
