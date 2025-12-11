#!/bin/bash
# Apply database migration to fix button_events table

echo "🔧 Applying button_events migration..."
echo "================================================"

cd ~/smart-heaven-v2/backend || exit 1

echo ""
echo "Running Alembic migration..."
docker exec smart-heaven-backend alembic upgrade head

echo ""
echo "✅ Migration completed!"
echo ""
echo "Testing button event creation..."
docker exec smart-heaven-backend python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.repositories.button_event_repo import ButtonEventRepository
from datetime import datetime

async def test():
    engine = create_async_engine('mysql+aiomysql://smartheaven:Smartheaven2024!@192.168.31.153:3306/smartheaven')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        repo = ButtonEventRepository(session)
        event = await repo.create_event(
            device='TEST_DEVICE',
            button='TEST_BUTTON',
            action='press',
            origin='test'
        )
        await session.commit()
        print(f'✅ Test event created with ID: {event.id}')

asyncio.run(test())
"

echo ""
echo "================================================"
echo "✅ All done! MQTT buttons should now work."
echo "Press a physical button to test."
