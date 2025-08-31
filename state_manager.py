from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_core.runnables.graph_mermaid import draw_mermaid_png
from IPython.display import Image, display
import utils

# Configure logging
logger = utils.set_logger(__name__)

class StateManager:
    def __init__(self, student_id):
        self.student_id = str(student_id)
        self.MONGODB_URI = "mongodb://172.16.0.177:27017/"
        self.DB_NAME = "amc8_math"
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
            utils.log("Saving state to MongoDB...", logger, 1)
            checkpointer.put(self.write_config, state, {}, {})
            utils.log("State successfully stored to MongoDB!", logger, 1)

    def retrieve(self):
        utils.log("Retrieving state from MongoDB...", logger, 1)
        with MongoDBSaver.from_conn_string(self.MONGODB_URI, self.DB_NAME) as checkpointer:
            utils.log("State successfully retrieved from MongoDB!", logger, 1)
            return checkpointer.get(self.read_config)

    def build_graph_redis(self, graph_builder):
        utils.log("Building Graph...", logger, 1)
        with RedisSaver.from_conn_string(self.REDIS_URI) as checkpointer:
            checkpointer.setup()
            graph = graph_builder.compile(checkpointer=checkpointer)
        #graph_img = display(Image(graph.get_graph().draw_mermaid_png(output_file_path="./graph.png")))
        #utils.log(graph_img, logger, 2)

        utils.log("Graph successfully built!", logger, 1)

        return graph

    def get_redis_state(self):
        utils.log("Retrieving redis state...", logger, 1)
        with RedisSaver.from_conn_string(self.REDIS_URI) as checkpointer:
            utils.log("Redis state retrieved!", logger, 1)
            return checkpointer.get(self.read_config)

    def clear_redis_memory(self):
        try:
            with RedisSaver.from_conn_string(self.REDIS_URI) as checkpointer:
                # Clear the specific thread's checkpoint data
                checkpointer.delete_thread(self.student_id)
                utils.log(f"Cleared Redis memory for student {self.student_id}", logger, 1)
        except Exception as e:
            utils.log(f"Warning: Could not clear Redis memory: {e}", logger, 1)

    def default_state(self):
        def_state = {"classification": None, 
                     "init_learning_objective": next(iter(utils.knowledge_graph)), 
                     "cur_learning_objective": next(iter(utils.knowledge_graph)), 
                     "learning_status": "steady", 
                     "student_id": self.student_id, 
                     "lesson_state": {'START_LESSON': 'In Progress','CONCEPT_INTRODUCTION': 'Not Done', 'GIVE_EASIER_PROBLEM': 'Not Done','PROBLEM_WALKTHROUGH': 'Not Done','GIVE_HARDER_PROBLEM': 'Not Done','END_LESSON': 'Not Done'}, 
                     "messages": [], 
                     "evaluator_grade": None, 
                     "evaluator_solution": None, 
                     "bkt_graph": utils.knowledge_graph, 
                     "math_context": None, 
                     "personality_context": None}
        return def_state