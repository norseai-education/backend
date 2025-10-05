from langgraph.checkpoint.mongodb import MongoDBSaver
from src.utils import logging, utils

class UserGraphService:
    def __init__(self):
        self.MONGODB_URI = "mongodb://172.16.0.177:27019/"
        self.DB_NAME = "norseai"
        self.logger = logging.set_logger(__name__)

    async def get(self, student_id: int):
        with MongoDBSaver.from_conn_string(self.MONGODB_URI, self.DB_NAME) as checkpointer:
            return list(checkpointer.list({"configurable": {"thread_id": str(student_id)}}))[-1].checkpoint.get("bkt_graph")

    async def update(self, student_id: int, user_graph: dict):
        with MongoDBSaver.from_conn_string(self.MONGODB_URI, self.DB_NAME) as checkpointer:
            state = {}
            state["id"] = student_id
            state["cur_learning_objective"] = utils.get_learning_obj(user_graph)
            state["bkt_graph"] = user_graph
            return checkpointer.put({"configurable": {"thread_id": str(student_id), "checkpoint_ns": ""}}, state, {}, {})

    async def delete(self, student_id: int):
        with MongoDBSaver.from_conn_string(self.MONGODB_URI, self.DB_NAME) as checkpointer:
            return checkpointer.delete_thread({"configurable": {"thread_id": str(student_id)}})