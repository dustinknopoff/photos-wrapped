import os
import osxphotos
import json
import argparse

from photos_wrapped.config import ASSETS_DIR_NOT_TRACKED
from photos_wrapped.highlights_ml import generate_highlights
from photos_wrapped.photos import get_and_sort


def run():
    parser = argparse.ArgumentParser("remove_highlight_dupes")
    parser.add_argument(
        "--year", dest="year", help="The year to recompute", type=int, required=True
    )
    args = parser.parse_args()
    if not os.path.isfile(f"{args.year}.json"):
        raise ValueError("You need to generate the stats first")
    photosdb = osxphotos.PhotosDB()

    photos = get_and_sort(photosdb, args.year, ASSETS_DIR_NOT_TRACKED)
    highlights = generate_highlights(photos)
    stats = {}
    with open(f"{args.year}.json", "r") as f:
        stats = json.load(f)
        stats["photo_highlights"] = highlights
    with open(f"{args.year}.json", "w") as f:
        json.dump(stats, f)


if __name__ == "__main__":
    run()
