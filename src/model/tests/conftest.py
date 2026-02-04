from pathlib import Path
import sys

path = Path(__file__).parent.parent.parent
sys.path.append(str(path))