import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.routers import algo_router, backtest_router, data_router, strategy_router
from fastapi.responses import FileResponse


app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    algo_router.router,
    tags=["Algo"],
    responses={404: {"description": "Not found"}},
)
app.include_router(
    data_router.router,
    tags=["Data"],
    responses={404: {"description": "Not found"}},
)
app.include_router(
    strategy_router.router,
    tags=["Strategy"],
    responses={404: {"description": "Not found"}},
)
app.include_router(
    backtest_router.router,
    tags=["Backtest"],
    responses={404: {"description": "Not found"}},
)

app.mount("/", StaticFiles(directory="./static/build", html=True), name="static")


# If url not found in backend, pass to frontend.
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    return FileResponse("./static/build/index.html")

if __name__ == "__main__":
    uvicorn.run("src.main:app", port=5000, host="0.0.0.0", log_level="info")
