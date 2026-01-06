
import asyncio
from sqlalchemy import text
from app.database import engine

async def check_columns():
    print("Checking columns in 'users' table...")
    async with engine.begin() as conn:
        try:
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='users'"
            ))
            columns = [row[0] for row in result.fetchall()]
            print(f"Columns: {columns}")
            
            if 'department_id' not in columns:
                print("MISSING: 'department_id' column")
            else:
                print("FOUND: 'department_id' column")
                
        except Exception as e:
            print(f"Check failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_columns())
