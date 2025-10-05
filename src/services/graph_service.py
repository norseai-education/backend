from backend.src.services.MongoDBHandler import MongoDBHandler
from backend.src.config.settings import settings

class UserGraphService:
    def __init__(self):
        self.db = MongoDBHandler(settings.mongodb_url)
        self.db.connect("norseai")

    async def get(self, student_id: int):
        return self.db.find_documents('checkpoint_writes', {"thread_id": str(student_id)})

    async def update(self, student_id: int, user_graph: dict):
        return self.db.update_document('checkpoint_writes', {"thread_id": str(student_id)}, {"user_graph": user_graph})

    async def delete(self, student_id: int):
        return self.db.delete_document('checkpoint_writes', {"thread_id": str(student_id)})