from backend.src.services.MongoDBHandler import MongoDBHandler

class UserGraphService:
    def __init__(self):
        self.db = MongoDBHandler("mongodb://172.16.0.177:27019/")
        self.db.connect("norseai")

    async def get(self, student_id: int):
        return self.db.find_documents('checkpoint_writes', {"thread_id": str(student_id)})

    async def update(self, student_id: int, user_graph: dict):
        return self.db.update_document('checkpoint_writes', {"thread_id": str(student_id)}, {"user_graph": user_graph})

    async def delete(self, student_id: int):
        return self.db.delete_document('checkpoint_writes', {"thread_id": str(student_id)})