from __future__ import annotations
from collections import Counter
from pillow_heif import register_heif_opener

from typing import List, Tuple, TypedDict
import osxphotos

from photos_wrapped.convert import convert_to_jpeg
from photos_wrapped.highlights_ml import generate_hdbscan_highlights

register_heif_opener()

num_month_to_display = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def count_by_year(photosdb: osxphotos.PhotosDB):
    for i in range(1945, 2025):
        query = osxphotos.QueryOptions(
            burst=False, screenshot=False, photos=True, year=[i]
        )
        print(f"{i} - {len(photosdb.query(query))}")


class StatsTypes(TypedDict):
    selfies: int
    burst: int
    panorama: int
    favorite: int
    slow_mo: int
    time_lapse: int
    movie: int
    photo: int


class Stats(TypedDict):
    stats: StatsTypes
    labels: List[Tuple[str, int]]
    top_labels: List[Tuple[str, int]]
    locations: List[Tuple[str, int]]
    top_locations: List[Tuple[str, int]]
    people: List[Tuple[str, int]]
    top_people: List[Tuple[str, int]]
    months: List[Tuple[int, int]]
    cameras: List[str]
    camera_models: List[str]


def get_and_sort(photosdb: osxphotos.PhotosDB, year: int) -> List[osxphotos.PhotoInfo]:
    query = osxphotos.QueryOptions(photos=True, movies=True, year=[year])
    photos = photosdb.query(query)
    sorted_by_score = sorted(
        photos,
        key=lambda photo: photo.score.curation
        + photo.score.interesting_subject
        + photo.score.behavioral,
        reverse=True,
    )
    return sorted_by_score


def select_without_similar(
    photos: List[osxphotos.PhotoInfo], asset_dir: str, quantity: int = 20
) -> List[str]:
    results = []
    for photo in photos:
        path = convert_to_jpeg(photo, asset_dir)
        results.append(path)
        if len(results) == quantity:
            break
    return results


def stats_for_year(photosdb: osxphotos.PhotosDB, year: int, asset_dir: str) -> Stats:
    labels = Counter()
    cameras = set()
    camera_models = set()
    people = Counter()
    months = Counter()
    locations = Counter()
    person_to_photo = {}
    stats = {
        "selfies": 0,
        "burst": 0,
        "panorama": 0,
        "favorite": 0,
        "slow_mo": 0,
        "time_lapse": 0,
        "movie": 0,
        "photo": 0,
    }
    photos = get_and_sort(photosdb, year)
    photo_highlights = generate_hdbscan_highlights(photos)

    for photo in photos:
        for label in photo.labels_normalized:
            labels[label] += 1
        for person in photo.person_info:
            if person.name != "_UNKNOWN_":
                if people[person.name] == 0 and person.keyphoto:
                    filename = convert_to_jpeg(person.keyphoto, asset_dir)
                    person_to_photo[person.name] = filename
                people[person.name] += 1
        if photo.exif_info.camera_make:
            cameras.add(photo.exif_info.camera_make)
            camera_models.add(photo.exif_info.camera_model)
        if photo.place:
            locations[f"{photo.place.address.city} {photo.place.address.country}"] += 1
        months[photo.date.month] += 1
        if photo.selfie:
            stats["selfies"] += 1
        if photo.burst:
            stats["burst"] += 1
        if photo.panorama:
            stats["panorama"] += 1
        if photo.favorite:
            stats["favorite"] += 1
        if photo.slow_mo:
            stats["slow_mo"] += 1
        if photo.time_lapse:
            stats["time_lapse"] += 1
        if photo.ismovie:
            stats["movie"] += 1
        else:
            stats["photo"] += 1

    return {
        "stats": stats,
        "cameras": list(cameras),
        "camera_models": list(camera_models),
        "locations": locations,
        "labels": labels,
        "top_locations": locations.most_common(10),
        "top_labels": labels.most_common(10),
        "months": [
            (num_month_to_display[month], months[month]) for month in range(1, 13)
        ],
        "people": people,
        "top_people": people.most_common(10),
        "person_to_photo": person_to_photo,
        "photo_highlights": photo_highlights,
    }
