from src.services.ChromaDBHandler import ChromaDBHandler
from src.services.MongoDBHandler import MongoDBHandler
from src.services.models import embedding_model
from src.utils import logging
from bson import ObjectId

# Configure logging
logger = logging.set_logger(__name__)

# print("Connecting to chromadb...")
# chroma_handler = ChromaDBHandler()
# print(chroma_handler.list_collections())
# print("Successfully connected to chromadb...\n")
# print("------------------------------------------")
# print("Connecting to mongodb...")
# mongo_handler = MongoDBHandler("mongodb://172.16.0.177:27019")
# mongo_handler.connect("amc8_database")
# print("Successfully connected to mongodb...")

class TextToVec:
    """
    This class is used to convert text to vectors and add them to chromadb. 
    change mongo_collection_name to change the collection to convert to vectors.
    change chroma_collection_name to change the collection to add the vectors to.
    """
    def __init__(self):
        self.mongo_handler = MongoDBHandler("mongodb://172.16.0.177:27019")
        self.mongo_handler.connect("amc8_database")
        self.chroma_handler = ChromaDBHandler()
        # self.mongo_documents = mongo_handler.find_documents(self.mongo_collection_name)
        # self.chroma_documents = chroma_handler.get_collection(self.chroma_collection_name)
        self.embedding_model = embedding_model

    def need_to_transfer(self, mongo_db_name: str, chroma_db_name: str):
        ids = []
        documents = self.mongo_handler.find_documents(mongo_db_name)
        collection = self.chroma_handler.get_collection(chroma_db_name)
        for document in documents:
            if str(document["_id"]) not in collection.get()["ids"]:
                ids.append(str(document["_id"]))
        return ids

    def problem_to_vec(self):
        document_list = []
        ids = []
        metadata = []
        ids = self.need_to_transfer("problems", "AMC8_problems")
        collection = self.chroma_handler.get_collection("AMC8_problems")
        for id in ids:
            document = self.mongo_handler.find_documents("problems", {"_id":ObjectId(id)})
            document_list.append(document["problem"])
            ids.append(str(document["_id"]))
            del document["problem"]
            del document["_id"]
            change_concepts = ''
            for concept in document["concepts"]:
                change_concepts += concept + ','
            if change_concepts[-1] == ',':
                change_concepts = change_concepts[:-1]
            document["concepts"] = change_concepts
            if "last_updated" in document:
                del document["last_updated"]
            metadata.append(document)

        try:
            logging.log("adding all documents to chromadb...", logger, 2)
            collection.add_documents(collection_name="problems", documents=document_list, ids=ids, metadatas=metadata, embedding_model=self.embedding_model)
            logging.log("Successfully added all documents to chromadb...", logger, 2)
        except Exception as e:
            logging.log(f"Error adding documents to chromadb: {e}", logger, 0)

    def math_related_to_vec(self):
        document_list = []
        ids = []
        metadata = []
        ids = self.need_to_transfer("math_related", "math_related")
        collection = self.chroma_handler.get_collection("math_related")
        for id in ids:
            document = self.mongo_handler.find_documents("math_related", {"_id":ObjectId(id)})
            document_list.append(document["content"])
            ids.append(str(document["_id"]))
            metadata.append({"student_id": document["student_id"]})
        try:
            logging.log("adding all documents to chromadb...", logger, 2)
            collection.add_documents(collection_name="math_related", documents=document_list, ids=ids, metadatas=metadata, embedding_model=self.embedding_model)
            logging.log("Successfully added all documents to chromadb...", logger, 2)
        except Exception as e:
            logging.log(f"Error adding documents to chromadb: {e}", logger, 0)

    def student_persona_to_vec(self):
        document_list = []
        ids = []
        metadata = []
        ids = self.need_to_transfer("student_persona", "student_persona")
        collection = self.chroma_handler.get_collection("student_persona")
        for id in ids:
            document = self.mongo_handler.find_documents("student_persona", {"_id":ObjectId(id)})
            document_list.append(document["content"])
            ids.append(str(document["_id"]))
            metadata.append({"student_id": document["student_id"]})
        try:
            logging.log("adding all documents to chromadb...", logger, 2)
            collection.add_documents(collection_name="student_persona", documents=document_list, ids=ids, metadatas=metadata, embedding_model=self.embedding_model)
            logging.log("Successfully added all documents to chromadb...", logger, 2)
        except Exception as e:
            logging.log(f"Error adding documents to chromadb: {e}", logger, 0)

    def conversation_history_to_vec(self):
        document_list = []
        ids = []
        metadata = []
        ids = self.need_to_transfer("conversation_history", "conversation_history")
        collection = self.chroma_handler.get_collection("conversation_history")
        for id in ids:
            document = self.mongo_handler.find_documents("conversation_history", {"_id":ObjectId(id)})
            document_list.append(document["content"])
            ids.append(str(document["_id"]))
            metadata.append({"student_id": document["student_id"], "role": document["role"]})
        try:
            logging.log("adding all documents to chromadb...", logger, 2)
            collection.add_documents(collection_name="conversation_history", documents=document_list, ids=ids, metadatas=metadata, embedding_model=self.embedding_model)
            logging.log("Successfully added all documents to chromadb...", logger, 2)
        except Exception as e:
            logging.log(f"Error adding documents to chromadb: {e}", logger, 0)

    def amc8_math_to_vec(self):
        document_list = []
        ids = []
        metadata = []
        ids = self.need_to_transfer("AMC8_math", "AMC8_math")
        collection = self.chroma_handler.get_collection("AMC8_math")
        for id in ids:
            document = self.mongo_handler.find_documents("AMC8_math", {"_id":ObjectId(id)})
            document_list.append(document["text"])
            ids.append(str(document["_id"]))
        try:
            logging.log("adding all documents to chromadb...", logger, 2)
            collection.add_documents(collection_name="AMC8_math", documents=document_list, ids=ids, embedding_model=self.embedding_model)
            logging.log("Successfully added all documents to chromadb...", logger, 2)
        except Exception as e:
            logging.log(f"Error adding documents to chromadb: {e}", logger, 0)

# test = TextToVec()
# test.problem_to_vec()

# test = TextToVec(mongo_collection_name="math_related", chroma_collection_name="math_related")
# test.math_related_to_vec()

# test = TextToVec(mongo_collection_name="student_persona", chroma_collection_name="student_persona")
# test.student_persona_to_vec()

# test = TextToVec(mongo_collection_name="conversation_history", chroma_collection_name="conversation_history")
# test.conversation_history_to_vec()

# test = TextToVec(mongo_collection_name="AMC8_math", chroma_collection_name="AMC8_math")
# test.amc8_math_to_vec()