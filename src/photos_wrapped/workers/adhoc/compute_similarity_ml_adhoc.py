from itertools import batched
import logging
import os
from typing import List, Optional
import osxphotos
import json
import argparse
from PIL import Image

from photos_wrapped.config import ASSETS_DIR_NOT_TRACKED
from photos_wrapped.convert import convert_to_jpeg
from photos_wrapped.photo_similarity import calculate_duplicates
from photos_wrapped.photos import get_and_sort


def generate_clip_highlights(
    photos: List[osxphotos.PhotoInfo], length: Optional[int] = 20
) -> List[str]:
    highlights = []
    for batch in batched(photos, 20):
        poison_set = set()
        image_path_list = []
        for photo in batch:
            if photo.ismovie:
                continue
            image_path_list.append(
                convert_to_jpeg(photo, asset_dir=ASSETS_DIR_NOT_TRACKED)
            )
        image_obj_list = [Image.open(photo) for photo in image_path_list]
        duplicates = calculate_duplicates(image_obj_list)
        for _, _, image_id2 in duplicates:
            poison_set.add(image_path_list[image_id2])
            try:
                logging.info(f"Deleting {image_path_list[image_id2]}")
                os.remove(image_path_list[image_id2])
            except FileNotFoundError:
                pass
        for image in image_path_list:
            if image not in poison_set and len(highlights) < 20:
                highlights.append(image)
        if len(highlights) == length:
            break
        logging.info(f"Current length of highlights: {len(highlights)}")
    return highlights


def run():
    parser = argparse.ArgumentParser("remove_highlight_dupes")
    parser.add_argument(
        "--year", dest="year", help="The year to recompute", type=int, required=True
    )
    args = parser.parse_args()
    if not os.path.isfile(f"{args.year}.json"):
        raise ValueError("You need to generate the stats first")
    photosdb = osxphotos.PhotosDB()

    photos = get_and_sort(photosdb, args.year)
    highlights = generate_clip_highlights(photos)
    stats = {}
    with open(f"{args.year}.json", "r") as f:
        stats = json.load(f)
        stats["photo_highlights"] = highlights
    with open(f"{args.year}.json", "w") as f:
        json.dump(stats, f)


if __name__ == "__main__":
    run()
