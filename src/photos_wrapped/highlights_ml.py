import os
from typing import List, Optional
from itertools import batched
import osxphotos
from PIL import Image
import logging

from photos_wrapped.config import ASSETS_DIR_NOT_TRACKED
from photos_wrapped.photo_similarity import calculate_duplicates
from photos_wrapped.photos import convert_to_jpeg


def generate_highlights(photos: List[osxphotos.PhotoInfo], length: Optional[int]=20) -> List[str]:
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
