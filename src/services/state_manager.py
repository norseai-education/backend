from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_core.runnables.graph_mermaid import draw_mermaid_png
from src.utils import logging
from src.utils import knowledge_info

# Configure logging
logger = logging.set_logger(__name__)

class StateManager:
    def __init__(self, student_id):
        self.student_id = str(student_id)
        self.MONGODB_URI = "mongodb://172.16.0.177:27019/"
        self.DB_NAME = "norseai"
        self.REDIS_URI = "redis://172.16.0.177:6379/"
        self.write_config = {"configurable": {"thread_id": self.student_id, "checkpoint_ns": ""}}
        self.read_config = {"configurable": {"thread_id": self.student_id}}


    def format_store(self, dict):
        store_dict = {}
        store_dict["id"] = self.student_id
        store_dict["cur_learning_objective"] = dict["cur_learning_objective"]
        store_dict["bkt_graph"] = dict["bkt_graph"]
        return store_dict

    def store(self, user_state):
        state = self.format_store(user_state)
        with MongoDBSaver.from_conn_string(self.MONGODB_URI, self.DB_NAME) as checkpointer:
            logging.log("Saving state to MongoDB...", logger, 1)
            checkpointer.put(self.write_config, state, {}, {})
            logging.log("State successfully stored to MongoDB!", logger, 1)

    def retrieve(self):
        logging.log("Retrieving state from MongoDB...", logger, 1)
        with MongoDBSaver.from_conn_string(self.MONGODB_URI, self.DB_NAME) as checkpointer:
            # logging.log("State successfully retrieved from MongoDB!", logger, 1)
            return checkpointer.get(self.read_config)

    def build_graph_redis(self, graph_builder):
        logging.log("Building Graph...", logger, 1)
        with RedisSaver.from_conn_string(self.REDIS_URI) as checkpointer:
            checkpointer.setup()
            graph = graph_builder.compile(checkpointer=checkpointer)
        #graph_img = display(Image(graph.get_graph().draw_mermaid_png(output_file_path="./graph.png")))
        #logging.log(graph_img, logger, 2)

        logging.log("Graph successfully built!", logger, 1)

        return graph

    def get_redis_state(self):
        logging.log("Retrieving redis state...", logger, 1)
        with RedisSaver.from_conn_string(self.REDIS_URI) as checkpointer:
            logging.log("Redis state retrieved!", logger, 1)
            return checkpointer.get(self.read_config)

    def clear_redis_memory(self):
        try:
            with RedisSaver.from_conn_string(self.REDIS_URI) as checkpointer:
                # Clear the specific thread's checkpoint data
                checkpointer.delete_thread(self.student_id)
                logging.log(f"Cleared Redis memory for student {self.student_id}", logger, 1)
        except Exception as e:
            logging.log(f"Warning: Could not clear Redis memory: {e}", logger, 1)

    def default_state(self):
        def_state = {"classification": None, 
                     "init_learning_objective": next(iter(knowledge_info.amc8_knowledge_graph)), 
                     "cur_learning_objective": next(iter(knowledge_info.amc8_knowledge_graph)), 
                     "learning_status": "steady", 
                     "student_id": self.student_id, 
                     "lesson_state": {'START_LESSON': 'In Progress', 'GIVE_PROBLEM': 'Not Done','PROBLEM_WALKTHROUGH': 'Not Done','GIVE_PROBLEM': 'Not Done', 'PROBLEM_WALKTHROUGH': 'Not Done','END_LESSON': 'Not Done'}, 
                     "messages": [], 
                     "evaluator_grade": None, 
                     "evaluator_solution": None, 
                     "bkt_graph": knowledge_info.amc8_knowledge_graph, 
                     "math_context": None, 
                     "personality_context": None}
        return def_state