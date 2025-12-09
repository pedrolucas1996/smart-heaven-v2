"""
Script para testar inserção manual de evento de botão no banco.
"""
import asyncio
from datetime import datetime
from pathlib import Path
import sys

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.repositories.button_event_repo import ButtonEventRepository

# Configuração do banco (ajuste se necessário)
DATABASE_URL = "mysql+aiomysql://pedro:395967@192.168.31.153:3306/smartheaven"
engine = create_async_engine(DATABASE_URL, echo=True)

async def main():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        repo = ButtonEventRepository(session)
        event = await repo.create_event(
            device="Base_D",
            button="S_Entrada",
            action="press",
            origin="manual_test",
            rssi=55,
            data_hora=datetime.utcnow()
        )
        await session.commit()
        print(
            "Evento inserido:",
            {
                "id": event.id,
                "device": event.device,
                "button": event.button,
                "action": event.action,
                "timestamp": event.data_hora,
            }
        )

if __name__ == "__main__":
    asyncio.run(main())
