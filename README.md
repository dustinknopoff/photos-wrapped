# Photos Wrapped

Spotify Wrapped for your Apple Photos Library.

![](Sample%20Wrapped.png)

Uses `osxphotos` to extract from your photo library the following stats:

- Most frequent labelled people in your pictures for a given year
- Number of photos, videos, cities photos were taken in, and cameras that were used
- Top 10 cities count of photos per city
- Photos taken broken down by month
- A word cloud of the top 120 identified attributes in photos
- A highlight reel of the Top 20 photos from the library (Specifically where Apple Photos has scored the photos highest for `curation`, `interesting_subject`, and `behavioral` values)

# How to Run

Use your preferred way to install python 3.12 and the dependencies defined in pyproject.toml

Or use [rye](https://rye.astral.sh) by running

```shell
rye sync
. ./venv/bin/activate
```

Then run 

```shell
fastapi run src/photos_wrapped/main.py
```

You should see

```
 ╭─────────── FastAPI CLI - Production mode ───────────╮
 │                                                     │
 │  Serving at: http://0.0.0.0:8000                    │
 │                                                     │
 │  API docs: http://0.0.0.0:8000/docs                 │
 │                                                     │
 │  Running in production mode, for development use:   │
 │                                                     │
 │  fastapi dev                                        │
 │                                                     │
 ╰─────────────────────────────────────────────────────╯
```

Go to URL shown for `Serving at:` The first load will take a long time!

http://0.0.0.0:8000 defaults to gathering information for 2023 but you can pass a year

http://0.0.0.0:8000/1992 and it will compute for that year.

The first run will save to disk the statistics and reuse every time from then onwards. If you'd like to force a rerun, you can provide the query parameter `force_reload` like to

http://0.0.0.0:8000/1992?force_reload=true

## All the Highlights look the same?


Sometimes, all of the photos selected to highlight end up being near duplicates which is not ideal. In that case, you can run a script to recompute using machine learning to determine near duplicate photos and skip those in the highlights.

```shell
python -m src.photos_wrapped.workers.adhoc.compute_similarity_ml_worker --year 1992
```

Refreshing the page will show the newly selected photos to highlight.

# Disclaimer

No guarantees on this breaking your photos library, but mine didn't during the entire development process. No destructive osxphotos calls are made.

Only 2 methods from osxphotos are used:
1. `query` to get all photos for a given year.
2. `export` to export the highlight photos and key photos for faces in a library. This does not remove them from your library.