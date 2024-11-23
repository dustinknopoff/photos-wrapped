

import json
import os
import osxphotos
from photos_wrapped.config import ASSETS_DIR_NOT_TRACKED
from photos_wrapped.photos import stats_for_year

from .photos import Stats, stats_for_year


def write_stats(year: int):
    photosdb = osxphotos.PhotosDB()
    stats = stats_for_year(
        photosdb=photosdb, year=year, asset_dir=ASSETS_DIR_NOT_TRACKED
    )

    with open(f"{year}.json", "w") as f:
        json.dump(stats, f)


def load_stats(year: int, force_reload: bool) -> Stats:
    if not os.path.isfile(f"{year}.json") or force_reload:
        write_stats(year)
    with open(f"{year}.json") as f:
        return json.load(f)