from fastapi import FastAPI, Request
import httpx
import logging
from logging_config import setup_logging
import uvicorn
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            response = Response(content=response_body, status_code=response.status_code, headers=dict(response.headers))
            logger.info(f"Response: {response.status_code}, Body: {response_body.decode()}")
            return response
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"message": "Internal Server Error"}
            )

app.add_middleware(LoggingMiddleware)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    logger.info(f"Proxying request: {request.method} {request.url}")
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"http://127.0.0.1:8001/{path}",
            headers=request.headers,
            content=await request.body()
        )
    logger.info(f"Received response from main service: {response.status_code}")
    return Response(content=response.content, status_code=response.status_code, headers=dict(response.headers))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
