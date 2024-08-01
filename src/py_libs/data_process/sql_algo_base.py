from ast import literal_eval

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.py_libs.objects.algo_types import AlgoInfo, AlgoStack

Base = declarative_base()
DATABASE_PATH = "algo_stack.db"


# SQLAlchemy Models
class AlgoInfoModel(Base):
    __tablename__ = "algo"

    id = Column(String, primary_key=True)
    content = Column(Text)
    algoType = Column(String)
    additional = Column(Text)


class AlgoStackModel(Base):
    __tablename__ = "stack"

    id = Column(String, primary_key=True)
    title = Column(Text)
    algoIds = Column(Text)


class AlgoStackOrderModel(Base):
    __tablename__ = "algo_stack_order"

    id = Column(Integer, primary_key=True)
    order = Column(Text)


def create_connection(db_file):
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    return engine


def create_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def insert_algo(session, algo: AlgoInfo):
    algo_model = AlgoInfoModel(
        id=algo.id, content=algo.content, algoType=algo.algoType, additional=str(algo.additional)
    )
    session.merge(algo_model)  # Use merge to handle both insert and update
    session.commit()


def get_algo(session, algo_id: str):
    algo_model = session.query(AlgoInfoModel).filter_by(id=algo_id).first()
    if algo_model:
        return AlgoInfo(
            id=algo_model.id,
            content=algo_model.content,
            algoType=algo_model.algoType,
            additional=literal_eval(algo_model.additional),
        )
    return None


def delete_algo(session, algo_id: str):
    session.query(AlgoInfoModel).filter_by(id=algo_id).delete()
    session.commit()


def insert_stack(session, stack: AlgoStack):
    stack_model = AlgoStackModel(id=stack.id, title=stack.title, algoIds=str(stack.algoIds))
    session.merge(stack_model)  # Use merge to handle both insert and update
    session.commit()


def get_stack(session, stack_id: str):
    stack_model = session.query(AlgoStackModel).filter_by(id=stack_id).first()
    if stack_model:
        return AlgoStack(
            id=stack_model.id, title=stack_model.title, algoIds=literal_eval(stack_model.algoIds)
        )
    return None


def delete_stack(session, stack_id: str):
    session.query(AlgoStackModel).filter_by(id=stack_id).delete()
    session.commit()


def insert_stack_order(session, stack_order: list):
    stack_order_model = AlgoStackOrderModel(order=str(stack_order))
    existing_order = get_stack_order(session)
    if existing_order:
        stack_order_model = (
            session.query(AlgoStackOrderModel).order_by(AlgoStackOrderModel.id.desc()).first()
        )
        stack_order_model.order = str(stack_order)
        session.commit()
    else:
        session.add(stack_order_model)
        session.commit()


def get_stack_order(session):
    stack_order_model = (
        session.query(AlgoStackOrderModel).order_by(AlgoStackOrderModel.id.desc()).first()
    )
    if stack_order_model:
        return literal_eval(stack_order_model.order)
    return None


def clear_all_data(session):
    session.query(AlgoInfoModel).delete()
    session.query(AlgoStackModel).delete()
    session.query(AlgoStackOrderModel).delete()
    session.commit()


def get_all_data(session):
    algos = session.query(AlgoInfoModel).all()
    stacks = session.query(AlgoStackModel).all()

    algos_data = {
        algo.id: AlgoInfo(
            id=algo.id,
            content=algo.content,
            algoType=algo.algoType,
            additional=literal_eval(algo.additional),
        )
        for algo in algos
    }
    stacks_data = {
        stack.id: AlgoStack(id=stack.id, title=stack.title, algoIds=literal_eval(stack.algoIds))
        for stack in stacks
    }
    stack_orders_data = get_stack_order(session)

    return {"algos": algos_data, "algo_stack_info": stacks_data, "stack_order": stack_orders_data}


def init_session():
    engine = create_connection(DATABASE_PATH)
    session = create_session(engine)
    return session


def main():
    session = init_session()

    # Example usage
    algo = AlgoInfo(id="1", content="Test Algo", algoType="Type1")
    insert_algo(session, algo)
    algo = AlgoInfo(id="2", content="Test2 Algo", algoType="Type1")
    insert_algo(session, algo)
    algo = AlgoInfo(id="3", content="Test3 Algo", algoType="Type1")
    insert_algo(session, algo)

    retrieved_algo = get_algo(session, "1")
    print(retrieved_algo)

    algo.content = "Updated Algo"
    insert_algo(session, algo)

    delete_algo(session, "1")

    stack = AlgoStack(id="stack-1", title="Test Stack", algoIds=["1", "2"])
    insert_stack(session, stack)

    retrieved_stack = get_stack(session, "stack-1")
    print(retrieved_stack)

    stack.title = "Updated Stack"
    insert_stack(session, stack)

    delete_stack(session, "stack-1")

    stack_order = ["stack-1", "stack-2"]
    insert_stack_order(session, stack_order)

    retrieved_stack_order = get_stack_order(session)
    print(retrieved_stack_order)

    stack_order.append("stack-3")
    insert_stack_order(session, stack_order)

    retrieved_stack_order = get_stack_order(session)
    print(retrieved_stack_order)


if __name__ == "__main__":
    main()
