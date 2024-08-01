from ast import literal_eval

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.py_libs.objects.strategy_types import StrategyInfo

Base = declarative_base()
DATABASE_PATH = "strategy.db"


# SQLAlchemy Models


class StrategyModel(Base):
    __tablename__ = "strategy"

    id = Column(String, primary_key=True)
    stack_id = Column(Text)
    securities = Column(Text)
    additional = Column(Text)


class StrategyOrderModel(Base):
    __tablename__ = "strategy_order"

    id = Column(Integer, primary_key=True)
    order = Column(Text)


def create_connection(db_file):
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    return engine


def create_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def insert_strategy(session, strategy: StrategyInfo):
    strategy_model = StrategyModel(
        id=strategy.name,
        stack_id=strategy.stack_id,
        securities=str(strategy.securities),
        additional=str(strategy.additional),
    )
    session.merge(strategy_model)  # Use merge to handle both insert and update
    session.commit()


def get_strategy(session, strategy_id: str):
    strategy_model = session.query(StrategyModel).filter_by(id=strategy_id).first()
    if strategy_model:
        return {
            "id": strategy_model.id,
            "stackId": strategy_model.stack_id,
            "securities": literal_eval(strategy_model.securities),
            "additional": literal_eval(strategy_model.additional),
        }
    return None


def delete_strategy(session, strategy_id: str):
    session.query(StrategyModel).filter_by(id=strategy_id).delete()
    session.commit()


def insert_stack_order(session, strategy_order: list):
    strategy_order_model = StrategyOrderModel(order=str(strategy_order))
    existing_order = get_strategy_order(session)
    if existing_order:
        strategy_order_model = (
            session.query(StrategyOrderModel).order_by(StrategyOrderModel.id.desc()).first()
        )
        strategy_order_model.order = str(strategy_order)
        session.commit()
    else:
        session.add(strategy_order_model)
        session.commit()


def get_strategy_order(session):
    strategy_order_model = (
        session.query(StrategyOrderModel).order_by(StrategyOrderModel.id.desc()).first()
    )
    if strategy_order_model:
        return literal_eval(strategy_order_model.order)
    return None


def delete_strategy_order(session):
    session.query(StrategyOrderModel).delete()
    session.commit()


def clear_all_data(session):
    session.query(StrategyModel).delete()
    session.query(StrategyOrderModel).delete()
    session.commit()


def get_all_data(session):
    strategies = session.query(StrategyModel).all()

    strategy_data = {
        strategy.id: {
            "id": strategy.id,
            "stackId": strategy.stack_id,
            "securities": literal_eval(strategy.securities),
            "additional": literal_eval(strategy.additional),
        }
        for strategy in strategies
    }
    strategy_orders_data = get_strategy_order(session)

    return {"strategies": strategy_data, "strategy_order": strategy_orders_data}


def init_session():
    engine = create_connection(DATABASE_PATH)
    session = create_session(engine)
    return session


def main():
    session = init_session()

    # Insert example strategy
    strategy = StrategyInfo(
        name="strat-1",
        stack_id="stack-1",
        algo_stack=[],
        algo_ids=["algo-1", "algo-2"],
        securities=["AAPL", "GOOGL"],
        additional={"risk_level": "high", "target_return": 0.15},
    )
    insert_strategy(session, strategy)

    # Get the inserted strategy
    retrieved_strategy = get_strategy(session, "strat-1")
    print("Retrieved Strategy:", retrieved_strategy)

    # Update the strategy
    updated_strategy = StrategyInfo(
        name="strat-2",
        stack_id="stack-1",
        algo_stack=[],
        algo_ids=["algo-1", "algo-2"],
        securities=["AAPL", "GOOGL"],
        additional={"risk_level": "low", "target_return": 11.15},
    )
    insert_strategy(session, updated_strategy)

    # Get the updated strategy
    retrieved_strategy = get_strategy(session, "strat-1")
    print("Updated Strategy:", retrieved_strategy)

    # Insert strategy order
    strategy_order = ["strat-1", "strat-2"]
    insert_stack_order(session, strategy_order)

    # Get the strategy order
    retrieved_order = get_strategy_order(session)
    print("Retrieved Strategy Order:", retrieved_order)

    # Update strategy order
    strategy_order.append("strat-3")
    insert_stack_order(session, strategy_order)

    # Get the updated strategy order
    retrieved_order = get_strategy_order(session)
    print("Updated Strategy Order:", retrieved_order)

    # Get all data
    all_data = get_all_data(session)
    print("All Data:", all_data)

    # Clear all data
    clear_all_data(session)


if __name__ == "__main__":
    main()
