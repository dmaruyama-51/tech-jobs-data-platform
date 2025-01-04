import sys
from pathlib import Path

# プロジェクトルートディレクトリへのパスを取得
project_root = Path(__file__).parent.parent

# functionsディレクトリをPythonパスに追加
functions_dir = project_root / "functions"
sys.path.insert(0, str(functions_dir))

# func_scraper/utilsディレクトリをPythonパスに追加
func_scraper_utils = functions_dir / "func_scraper"
sys.path.insert(0, str(func_scraper_utils))

# sharedディレクトリをPythonパスに追加
shared_dir = functions_dir / "shared"
sys.path.insert(0, str(shared_dir))