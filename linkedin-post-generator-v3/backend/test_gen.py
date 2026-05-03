import traceback
import asyncio
from app.db.database import SessionLocal
from app.services.generation_service import GenerationService

async def test():
    db = SessionLocal()
    try:
        svc = GenerationService()
        res = await svc.generate_post('AI in 2026', "1", db)
        print(res)
    except Exception as e:
        traceback.print_exc()

asyncio.run(test())
