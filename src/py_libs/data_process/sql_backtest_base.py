from ast import literal_eval

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.py_libs.objects.backtest_types import BacktestInfo

Base = declarative_base()
DATABASE_PATH = "backtest.db"


# SQLAlchemy Models
class BacktestModel(Base):
    __tablename__ = "backtest"

    id = Column(String, primary_key=True)
    strategy_id = Column(Text)
    security_list = Column(Text)
    additional = Column(Text)


class BacktestOrderModel(Base):
    __tablename__ = "backtest_order"

    id = Column(Integer, primary_key=True)
    order = Column(Text)


def create_connection(db_file):
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    return engine


def create_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def insert_backtest(session, backtest: BacktestInfo):
    backtest_model = BacktestModel(
        id=backtest.name,
        strategy_id=backtest.strategy_id,
        security_list=str(backtest.security_list),
        additional=str(backtest.additional),
    )
    session.merge(backtest_model)  # Use merge to handle both insert and update
    session.commit()


def get_backtest(session, backtest_id: str):
    backtest_model = session.query(BacktestModel).filter_by(id=backtest_id).first()
    if backtest_model:
        return {
            "id": backtest_model.id,
            "strategy_id": backtest_model.strategy_id,
            "security_list": literal_eval(backtest_model.security_list),
            "additional": literal_eval(backtest_model.additional),
        }
    return None


def delete_backtest(session, backtest_id: str):
    session.query(BacktestModel).filter_by(id=backtest_id).delete()
    session.commit()


def insert_backtest_order(session, backtest_order: list):
    backtest_order_model = BacktestOrderModel(order=str(backtest_order))
    existing_order = get_backtest_order(session)
    if existing_order:
        backtest_order_model = (
            session.query(BacktestOrderModel).order_by(BacktestOrderModel.id.desc()).first()
        )
        backtest_order_model.order = str(backtest_order)
        session.commit()
    else:
        session.add(backtest_order_model)
        session.commit()


def get_backtest_order(session):
    backtest_order_model = (
        session.query(BacktestOrderModel).order_by(BacktestOrderModel.id.desc()).first()
    )
    if backtest_order_model:
        return literal_eval(backtest_order_model.order)
    return None


def delete_backtest_order(session):
    session.query(BacktestOrderModel).delete()
    session.commit()


def clear_all_data(session):
    session.query(BacktestModel).delete()
    session.query(BacktestOrderModel).delete()
    session.commit()


def get_all_data(session):
    backtests = session.query(BacktestModel).all()

    backtest_data = {
        backtest.id: {
            "id": backtest.id,
            "strategyId": backtest.strategy_id,
            "securityList": literal_eval(backtest.security_list),
            "additional": literal_eval(backtest.additional),
        }
        for backtest in backtests
    }
    backtest_orders_data = get_backtest_order(session)

    return {"backtests": backtest_data, "backtest_order": backtest_orders_data}


def init_session():
    engine = create_connection(DATABASE_PATH)
    session = create_session(engine)
    return session


# Example usage
def main():
    session = init_session()
    # Insert example backtest
    backtest = BacktestInfo(
        name="backtest-1",
        strategy=None,
        strategy_id="strategy-1",
        security_list=["AAPL", "GOOGL"],
        additional={"risk_level": "high", "target_return": 0.15},
    )
    insert_backtest(session, backtest)

    # Get the inserted backtest
    retrieved_backtest = get_backtest(session, "backtest-1")
    print("Retrieved Backtest:", retrieved_backtest)

    # Update the backtest
    updated_backtest = BacktestInfo(
        name="backtest-1",
        strategy=None,
        strategy_id="strategy-2",
        security_list=["MSFT", "AMZN"],
        additional={"risk_level": "medium", "target_return": 0.10},
    )
    insert_backtest(session, updated_backtest)

    # Get the updated backtest
    retrieved_backtest = get_backtest(session, "backtest-1")
    print("Updated Backtest:", retrieved_backtest)

    # Insert backtest order
    backtest_order = ["backtest-1", "backtest-2"]
    insert_backtest_order(session, backtest_order)

    # Get the backtest order
    retrieved_order = get_backtest_order(session)
    print("Retrieved Backtest Order:", retrieved_order)

    # Update backtest order
    backtest_order.append("backtest-3")
    insert_backtest_order(session, backtest_order)

    # Get the updated backtest order
    retrieved_order = get_backtest_order(session)
    print("Updated Backtest Order:", retrieved_order)

    # Get all data
    all_data = get_all_data(session)
    print("All Data:", all_data)

    # Clear all data
    clear_all_data(session)


if __name__ == "__main__":
    main()
