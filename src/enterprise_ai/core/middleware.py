import re
import uuid
from enterprise_ai.core.request_context import request_id_var

_VALID_ID = re.compile(r"^[A-Za-z0-9._:-]{1,100}$")

class RequestContextMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers", []))
        supplied = headers.get(b"x-request-id", b"").decode("latin-1")
        request_id = supplied if _VALID_ID.fullmatch(supplied) else str(uuid.uuid4())
        token = request_id_var.set(request_id)

        async def send_with_id(message):
            if message["type"] == "http.response.start":
                message["headers"] = list(message.get("headers", [])) + [
                    (b"x-request-id", request_id.encode("ascii"))]
            await send(message)
        try:
            await self.app(scope, receive, send_with_id)
        finally:
            request_id_var.reset(token)
