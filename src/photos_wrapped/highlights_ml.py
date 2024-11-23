from enum import Enum
import os
from typing import List, Optional
from itertools import batched
import osxphotos
from PIL import Image
import logging
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import StandardScaler

from photos_wrapped.config import ASSETS_DIR_NOT_TRACKED
from photos_wrapped.convert import convert_to_jpeg
from photos_wrapped.photo_similarity import calculate_duplicates


feature_names = [
    "overall",
    "curation",
    "behavioral",
    "interesting_subject",
]


class Strategy(Enum):
    CLIP = "clip"
    HDBSCAN = "hdbscan"


def generate_highlights(
    photos: List[osxphotos.PhotoInfo], strategy: Strategy, length: Optional[int] = 20
) -> List[str]:
    if strategy == Strategy.CLIP:
        return generate_clip_highlights(photos, length)
    else:
        return generate_hdbscan_highlights(photos, length)


def generate_hdbscan_highlights(
    photos: List[osxphotos.PhotoInfo], length: Optional[int] = 20
) -> List[str]:
    features = []
    for photo in photos:
        feature = []
        feature.append(photo.date.timestamp())
        feature.append(photo.latitude or 0)
        feature.append(photo.longitude or 0)
        feature.append(1 if photo.favorite else 0)
        feature.append(1 if len(photo.persons) > 0 else 0)
        scores = photo.score.asdict()
        for feature_name in feature_names:
            feature.append(scores[feature_name])
        features.append(feature)

    df = pd.DataFrame(features)

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df)

    kmeans = HDBSCAN()
    df["cluster"] = kmeans.fit_predict(scaled_features)

    clusters = set()
    count = 0
    image_path_list = []
    for idx, photo in enumerate(photos):
        if photo.ismovie:
            continue
        df_photo = df.iloc[idx]
        if int(df_photo["cluster"]) in clusters:
            logging.info("Skipping same cluster")
            continue
        clusters.add(int(df_photo["cluster"]))
        image_path_list.append(convert_to_jpeg(photo, asset_dir=ASSETS_DIR_NOT_TRACKED))
        count += 1
        if count >= length:
            break
    return image_path_list


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
