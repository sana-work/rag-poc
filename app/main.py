from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

@app.get("/")
async def read_index():
    return FileResponse("ui/index.html")

@app.get("/health")
def health_check():
    return {"status": "ok", "mode": settings.MODE, "retrieval": settings.RETRIEVAL_MODE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
