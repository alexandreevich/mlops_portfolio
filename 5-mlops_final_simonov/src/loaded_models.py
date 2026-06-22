import pickle
import pandas as pd

# from gensim.models import Word2Vec
from pathlib import Path


# Локальная загрузка моделей (вам необходимо будет это сделать в финальном решении при помощи S3).
with open(Path("./ranker.pkl"), "rb") as f:
    ranker = pickle.load(f)

# Локальная работа с базой данных (условная, конечно). Аналогично требуется сделать это при помощи S3.
# item_features = pd.read_parquet(Path("./item_features.parquet"))
BASE_DIR = Path.cwd()
# BASE_DIR = Path(__file__).resolve().parent.parent
# item_features = pd.read_parquet(BASE_DIR / "raw_data" / "item_features.parquet")
item_features = pd.read_parquet(BASE_DIR / "item_features.parquet")
