import osxphotos
from pillow_heif import register_heif_opener

from photos_wrapped.config import ASSETS_DIR_NOT_TRACKED
from photos_wrapped.convert import convert_to_jpeg
from photos_wrapped.photos import get_and_sort

register_heif_opener()

photosdb = osxphotos.PhotosDB()

photos = get_and_sort(photosdb, 2023)

import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import StandardScaler

feature_names = [
    "overall",
    "curation",
    "behavioral",
    "interesting_subject",
]

features = []
index_mapper = {}
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
    index_mapper[len(features) - 1] = photo.original_filename


df = pd.DataFrame(features)

scaler = StandardScaler()
scaled_features = scaler.fit_transform(df)

kmeans = HDBSCAN()
df["cluster"] = kmeans.fit_predict(scaled_features)

clusters = set()
count = 0
for idx, photo in enumerate(photos):
    if photo.ismovie:
        continue
    df_photo = df.iloc[idx]
    if int(df_photo["cluster"]) in clusters:
        continue
    clusters.add(int(df_photo["cluster"]))
    print(photo.original_filename)
    # print(convert_to_jpeg(photo, asset_dir=ASSETS_DIR_NOT_TRACKED))
    count += 1
    if count >= 20:
        break
