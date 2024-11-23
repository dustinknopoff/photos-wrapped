from typing import Union
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from photos_wrapped.config import ASSETS_DIR_NOT_TRACKED, STATIC_DIR, TEMPLATES_DIR
from .photos import Stats, stats_for_year
from photos_wrapped.database import initialize_if_not_exists
import osxphotos
import json
import os

default_year = 2023
initialize_if_not_exists()

templates = Jinja2Templates(directory=TEMPLATES_DIR)


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


app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.mount("/tmp_assets", StaticFiles(directory=ASSETS_DIR_NOT_TRACKED), name="persons")


@app.get("/")
def index(request: Request):
    context = load_stats(default_year, False)
    context["year"] = default_year
    return templates.TemplateResponse(
        request=request, name="index.jinja", context=context
    )


@app.get("/{year}")
def index(
    request: Request, year: Union[int, None] = default_year, force_reload: bool = False
):
    context = load_stats(year or default_year, force_reload=force_reload)
    context["year"] = year or default_year
    return templates.TemplateResponse(
        request=request, name="index.jinja", context=context
    )
