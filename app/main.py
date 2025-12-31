from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.api.routes import router
from app.config import settings

app = FastAPI(title="RAG PoC Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Mount UI Files
ui_dir = (settings.BASE_DIR / "ui").resolve()

app.mount("/static", StaticFiles(directory=str(ui_dir)), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    fav_file = ui_dir / "favicon.ico"
    if fav_file.exists():
        return FileResponse(str(fav_file))
    return JSONResponse({"detail": "not found"}, status_code=404)

@app.get("/")
async def read_index():
    index_file = ui_dir / "index.html"
    if not index_file.exists():
        return JSONResponse({
            "error": "UI files missing", 
            "checked_path": str(index_file),
            "base_dir": str(settings.BASE_DIR)
        }, status_code=404)
    return FileResponse(str(index_file), headers={"X-UI-Path": str(index_file)})

@app.get("/health")
def health_check():
    return {"status": "ok", "mode": settings.MODE, "retrieval": settings.RETRIEVAL_MODE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
