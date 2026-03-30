from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from .config import get_settings


class AuthMiddleware(BaseHTTPMiddleware):
    """Redirects unauthenticated requests to the login page."""

    OPEN_PATHS = {"/login", "/logout", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in self.OPEN_PATHS or path.startswith("/static"):
            return await call_next(request)
        if not request.session.get("user"):
            return RedirectResponse(url="/login", status_code=303)
        return await call_next(request)


def verify_credentials(username: str, password: str) -> bool:
    settings = get_settings()
    return username == settings.admin_username and password == settings.admin_password
