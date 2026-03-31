from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .config import get_settings
from .database import init_db
from .routers import public

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=settings.app_name, docs_url=None, redoc_url=None)

# --- Middleware ---
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# --- Static files & templates ---
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.state.templates = templates

# --- Public marketing site ---
app.include_router(public.router)


# --- Startup ---
@app.on_event("startup")
async def on_startup():
    init_db()
