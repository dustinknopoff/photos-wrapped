import json
from typing import Annotated
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Depends, FastAPI, HTTPException, Query
from contextlib import asynccontextmanager

from pydantic import BaseModel

from photos_wrapped.config import ASSETS_DIR_NOT_TRACKED, STATIC_DIR, TEMPLATES_DIR
from photos_wrapped.database import Queue, Status, create_db_and_tables, SessionDep
from photos_wrapped.stats import load_stats
from photos_wrapped.database import engine


templates = Jinja2Templates(directory=TEMPLATES_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables(engine)
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.mount("/tmp_assets", StaticFiles(directory=ASSETS_DIR_NOT_TRACKED), name="persons")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.jinja", context={}
    )

class FormData(BaseModel):
    year: int


@app.post("/stats/new")
def create_stats(request: Request, form: Annotated[FormData, Form()], session: SessionDep):
    job = Queue(payload=json.dumps({ "year": form.year}))
    session.add(job)
    session.commit()
    session.refresh(job)
    return templates.TemplateResponse(request=request, name="loading.jinja", context = {
        "job_id": job.id,
        "year": form.year
    })

@app.get("/stats/status/{job_id}")
def stats_status(request: Request, job_id: int,session: SessionDep):
    job = session.get(Queue, job_id)
    year = json.loads(job.payload)["year"]
    if job.status == Status.COMPLETE:
        return templates.TemplateResponse(request=request, name="go.jinja", context = {
            "location": f"/{year}/0"
        })
    else:
        return templates.TemplateResponse(request=request, name="loading.jinja", context = {
            "job_id": job.id,
            "year": year
        })
    
@app.get("/{year}/{page}")
def present(request: Request, year: int, page: int):
    stats = load_stats(year, force_reload=False)
    context = stats
    context["year"] = year
    context["navigation"] = {}
    if page > 0:
        context["navigation"]["previous"] = page - 1
    if page < 4:
        context["navigation"]["next"] = page + 1
    return templates.TemplateResponse(request=request, name=f"present/{page}.jinja", context=context)