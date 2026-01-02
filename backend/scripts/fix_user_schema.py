import asyncio
import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

async def fix_schema():
    print("Checking 'users' table schema...")
    async with engine.begin() as conn:
        try:
            # Check for department_id
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='department_id'"
            ))
            if not result.scalar():
                print("Adding missing column: department_id")
                await conn.execute(text("ALTER TABLE users ADD COLUMN department_id UUID REFERENCES departments(department_id) ON DELETE SET NULL"))
            else:
                print("Column 'department_id' exists.")

            # Check for team
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='team'"
            ))
            if not result.scalar():
                print("Adding missing column: team")
                await conn.execute(text("ALTER TABLE users ADD COLUMN team VARCHAR(100)"))
            else:
                print("Column 'team' exists.")
                
            print("Schema check/fix complete.")
                
        except Exception as e:
            print(f"Schema fix failed: {e}")

if __name__ == "__main__":
    asyncio.run(fix_schema())
