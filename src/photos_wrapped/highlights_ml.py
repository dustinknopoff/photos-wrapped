from enum import Enum
from typing import List, Optional
import osxphotos
import logging
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import StandardScaler

from photos_wrapped.config import ASSETS_DIR_NOT_TRACKED
from photos_wrapped.convert import convert_to_jpeg


feature_names = [
    "overall",
    "curation",
    "behavioral",
    "interesting_subject",
]


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

