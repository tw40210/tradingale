import logging

from fastapi import APIRouter
from src.py_libs.controllers.algo_controller import AlgoStackController

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/algo")

try:
    algo_stacks_controller = AlgoStackController()
    algo_stacks_controller.load_from_db()
except Exception as e:
    logger.error(f"Having problem when load local DB: {e}\n " f"Set with initial data.")
    algo_stacks_controller = AlgoStackController()


@router.get("/fetchAlgoStacks")
def fetch_algo_stacks():
    logger.info(f"fetch_plot: {algo_stacks_controller.fetch_algo_stacks()}")
    return {"AlgoStacks": algo_stacks_controller.fetch_algo_stacks()}


@router.post("/deleteAlgo")
def delete_algo(req: dict):
    logger.info(req)
    return {"AlgoStacks": algo_stacks_controller.fetch_algo_stacks()}


@router.post("/updateAlgoStacks")
def update_algo_stacks(req: dict):
    data = req["algoStacksData"]
    algo_stacks_controller.update_algo_stacks(data)
    algo_stacks_controller.save_to_db()
    logger.info(f"fetch_plot: {algo_stacks_controller.fetch_algo_stacks()}")
    logger.info("algo_stacks saved in local db!")
    return {"AlgoStacks": algo_stacks_controller.fetch_algo_stacks()}
