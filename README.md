# FastAPI Proxy with Logging Middleware

Este projeto é uma aplicação FastAPI que atua como um proxy, encaminhando solicitações para outro serviço e registrando as solicitações e respostas usando um middleware personalizado.

## Estrutura do Projeto

- `main.py`: Arquivo principal da aplicação que define a API FastAPI, middleware e rotas.
- `logging_config.py`: Arquivo de configuração para setup de logging.
- `requirements.txt`: Arquivo de dependências do projeto.
- `README.md`: Este arquivo de documentação.

## Funcionalidades

- **Proxy de Requisições**: A aplicação proxy redireciona todas as requisições para um serviço backend localizado em `http://127.0.0.1:8001`.
- **Middleware de Logging**: Middleware personalizado que registra todas as requisições e respostas, incluindo métodos HTTP, URLs e corpos de resposta.
- **Tratamento de Erros**: Respostas de erro são capturadas e um status de erro genérico 500 é retornado em caso de exceções.

## Requisitos

- Python 3.10 ou superior
- FastAPI
- HTTPX
- Uvicorn
- AnyIO
- Logging (configuração personalizada)

## Instalação

1. Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2. Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Executando a Aplicação

1. Inicie a aplicação FastAPI:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

2. Acesse a aplicação no navegador ou use ferramentas como `curl` ou Postman para enviar requisições para `http://127.0.0.1:8000`.

## Exemplo de Uso

1. Acesse a rota raiz para verificar se a aplicação está funcionando:
    ```bash
    curl http://127.0.0.1:8000/
    ```

2. Envie uma requisição para qualquer outra rota para testar o proxy:
    ```bash
    curl -X GET http://127.0.0.1:8000/alguma-rota
    ```

## Estrutura de Código

### `main.py`

```python
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
