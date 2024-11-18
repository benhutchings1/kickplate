import uvicorn
from fastapi import FastAPI

from error_handling import add_error_handlers
from features.health.router import router as health_router
from features.graph.router import router as graph_router
from settings import settings

app = FastAPI()

add_error_handlers(app)
app.include_router(health_router)
app.include_router(graph_router)

if __name__ == "__main__":
    if settings.DEBUG_MODE:
        uvicorn.run("app:app", host="localhost", port=8080, reload=True)
