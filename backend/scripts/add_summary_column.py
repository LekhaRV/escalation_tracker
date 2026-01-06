import asyncio
import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

async def add_column():
    print("Migrating: Adding ai_summary column to complaints table...")
    async with engine.begin() as conn:
        try:
            # Check if column exists
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='complaints' AND column_name='ai_summary'"
            ))
            if result.scalar():
                print("Column 'ai_summary' already exists. Skipping.")
                return

            await conn.execute(text("ALTER TABLE complaints ADD COLUMN ai_summary TEXT"))
            print("Successfully added 'ai_summary' column.")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(add_column())
