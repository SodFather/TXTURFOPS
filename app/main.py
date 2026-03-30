from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .config import get_settings
from .database import init_db
from .auth import AuthMiddleware, verify_credentials
from .routers import customers, dashboard

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=settings.app_name, docs_url=None, redoc_url=None)

# --- Middleware (last-added = outermost = runs first) ---
app.add_middleware(AuthMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# --- Static files & templates ---
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.state.templates = templates


# --- Routers ---
app.include_router(dashboard.router)
app.include_router(customers.router)


# --- Auth routes ---
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if verify_credentials(username, password):
        request.session["user"] = username
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request, "login.html", {"error": "Invalid username or password"}
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# --- Startup ---
@app.on_event("startup")
async def on_startup():
    init_db()
