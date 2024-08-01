import logging

from fastapi import APIRouter
from src.py_libs.controllers.backtest_controller import BacktestController
from src.routers.data_router import data_controller
from src.routers.strategy_router import strategy_controller

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/backtest")
backtest_controller = BacktestController(
    strategy_controller=strategy_controller, data_controller=data_controller
)
backtest_controller.load_from_db()


@router.post("/updateBacktests")
def update_backtests(req: dict):
    backtest_controller.update_backtests(req["backtestsData"])
    backtest_controller.save_to_db()
    logger.info(f"fetch_plot: {backtest_controller.fetch_backtests()}")
    logger.info("Backtests saved in local db!")
    return {"MetaDataList": backtest_controller.fetch_backtests()}


@router.get("/runBacktests")
def run_backtests():
    report_dict = backtest_controller.run_backtests()

    return {"Report": report_dict}


@router.get("/fetchBacktests")
def fetch_backtests():
    logger.info(f"fetch_plot: {backtest_controller.fetch_backtests()}")

    return {"Backtests": backtest_controller.fetch_backtests()}
