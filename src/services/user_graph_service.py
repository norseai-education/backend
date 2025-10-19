from langgraph.checkpoint.mongodb import MongoDBSaver
from src.utils import logging, utils

class UserGraphService:
    def __init__(self):
        self.MONGODB_URI = "mongodb://172.16.0.177:27019/"
        self.DB_NAME = "norseai"
        self.logger = logging.set_logger(__name__)

    async def get(self, student_id: int):
        with MongoDBSaver.from_conn_string(self.MONGODB_URI, self.DB_NAME) as checkpointer:
            try:
                return list(checkpointer.list({"configurable": {"thread_id": str(student_id)}}))[-1].checkpoint.get("bkt_graph"), list(checkpointer.list({"configurable": {"thread_id": str(student_id)}}))[-1].checkpoint.get("cur_learning_objective")
            except Exception as e:
                logging.log(f"Failed to retrieve user graph for student {student_id}: {e}", self.logger, 0)
                return None

    async def get_close(self, student_id: int):
        with MongoDBSaver.from_conn_string(self.MONGODB_URI, self.DB_NAME) as checkpointer:
            try:
                learning_objective = list(checkpointer.list({"configurable": {"thread_id": str(student_id)}}))[-1].checkpoint.get("cur_learning_objective")
                graph = list(checkpointer.list({"configurable": {"thread_id": str(student_id)}}))[-1].checkpoint.get("bkt_graph")
                
                if not learning_objective or not graph:
                    return None
                
                # Convert graph to list of items to get ordered access
                graph_items = list(graph.items())
                
                # Find the index of the current learning objective
                current_index = None
                for i, (key, value) in enumerate(graph_items):
                    if key == learning_objective:
                        current_index = i
                        break
                
                if current_index is None:
                    return None
                
                # Get previous 4 and next 5 items
                start_index = max(0, current_index - 4)
                end_index = min(len(graph_items), current_index + 6)  # +6 because we want 5 items after current
                
                # Extract the slice and convert back to dictionary
                close_items = graph_items[start_index:end_index]
                result = dict(close_items)
                
                return result
                
            except Exception as e:
                logging.log(f"Failed to retrieve learning objective for student {student_id}: {e}", self.logger, 0)
                return None

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