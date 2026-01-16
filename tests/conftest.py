import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH для импортов
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
