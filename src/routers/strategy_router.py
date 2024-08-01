import logging

from fastapi import APIRouter
from src.py_libs.controllers.strategy_controller import StrategyController
from src.routers.algo_router import algo_stacks_controller

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/strategy")
strategy_controller = StrategyController(algo_stacks_controller)
strategy_controller.load_from_db()


@router.post("/updateStrategies")
def update_strategies(req: dict):
    strategy_controller.update_strategies(req["strategiesData"])
    strategy_controller.save_to_db()
    logger.info(f"fetch_plot: {strategy_controller.fetch_strategies()}")
    logger.info("Strategies saved in local db!")
    return {"MetaDataList": strategy_controller.fetch_strategies()}


@router.get("/fetchStrategies")
def fetch_strategies():
    logger.info(f"fetch_plot: {strategy_controller.fetch_strategies()}")
    return {"Strategies": strategy_controller.fetch_strategies()}
