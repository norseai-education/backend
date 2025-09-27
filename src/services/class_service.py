import asyncpg
import uuid


class ClassService:
    async def get_available_classes(self, conn: asyncpg.Connection):
        classes = await conn.fetch("SELECT id, class_name, description FROM classes")
        return classes

    async def get_user_classes(self, conn: asyncpg.Connection, student_id: int):
        classes = await conn.fetch("SELECT class_id, class_name, description FROM registration, classes WHERE registration.class_id = classes.id AND registration.student_id = $1",
            student_id
        )
        return classes
    
    async def register_class(self, conn: asyncpg.Connection, student_id: int, class_id: uuid.UUID):
        id = uuid.uuid4()
        await conn.execute("INSERT INTO registration (student_id, class_id, id) VALUES ($1, $2, $3)",
            student_id, class_id, id
        )
        return id
    
    async def remove_class(self, conn: asyncpg.Connection, student_id: int, class_id: uuid.UUID):
        await conn.execute("DELETE FROM registration WHERE student_id = $1 AND class_id = $2",
            student_id, class_id
        )
        return class_id

    async def create_class(self, conn: asyncpg.Connection, class_name: str, class_description: str):
        class_id = uuid.uuid4()
        await conn.execute("INSERT INTO classes (class_name, description, id) VALUES ($1, $2, $3)",
            class_name, class_description, class_id
        )
        return class_id