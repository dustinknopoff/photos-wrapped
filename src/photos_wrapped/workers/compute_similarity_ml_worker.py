import os
from sqlite3 import Connection
from typing import List
import polling
from pydantic import BaseModel
import osxphotos
import json

from photos_wrapped.config import ASSETS_DIR_NOT_TRACKED
from photos_wrapped.database import create_connection
from photos_wrapped.highlights_ml import generate_highlights
from photos_wrapped.photos import get_and_sort


class RequestV1(BaseModel):
    version: str = "1.0.0"
    type: str = "recompute_similarity"
    year: int


def load_open_requests(db: Connection):
    query = """SELECT * FROM jobs WHERE status == 0 AND json_extract(request, '$.type') == 'recompute_similarity' and json_extract(request, '$.version') == '1.0.0';"""
    return db.cursor().execute(query).fetchall()


def mark_complete(db: Connection, id: str, highlights: List[str]):
    query = """UPDATE jobs SET status = 1, response = ? WHERE uuid = ?;"""
    db.cursor().execute(query, (json.dumps(highlights), id))
    db.commit()


def run():
    photosdb = osxphotos.PhotosDB()
    db, cursor = create_connection()
    for job in load_open_requests(db):
        request = RequestV1.model_validate_json(job[1])
        photos = get_and_sort(photosdb, request.year, ASSETS_DIR_NOT_TRACKED)
        highlights = generate_highlights(photos)
        stats = {}
        with open(f"{request.year}.json", "r") as f:
            stats = json.load(f)
            stats["photo_highlights"] = highlights
        with open(f"{request.year}.json", "w") as f:
            json.dump(stats, f)
        mark_complete(db, job[0], highlights)
    db.close()


if __name__ == "__main__":
    if bool(os.environ.get("RUN_ONCE")):
        run()
    else:
        polling.poll(run, 5, poll_forever=True)
