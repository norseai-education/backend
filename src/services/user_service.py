import asyncpg
class UserService:
    async def get_student_id(self, conn: asyncpg.Connection, email: str):
        classes = await conn.fetch("SELECT student_id FROM users WHERE email = $1", email)
        if not classes: 
            next_student_id = await conn.fetchval(
                "SELECT COALESCE(MAX(student_id), 0) + 1 FROM users"
            )
            await conn.execute(
                "INSERT INTO users (student_id, email) VALUES ($1, $2)",
                next_student_id, email
            )
            return next_student_id
        return classes[0]['student_id']