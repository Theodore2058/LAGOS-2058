"""LAGOS-2058 Game Master API — FastAPI backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="LAGOS-2058 GM API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve GeoJSON files as static
geojson_dir = os.path.join(os.path.dirname(__file__), "..", "GeoJSON")
if os.path.isdir(geojson_dir):
    app.mount("/static/geojson", StaticFiles(directory=geojson_dir), name="geojson")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "engine": "lagos-2058"}
