"""Check button_events table schema."""
from sqlalchemy import inspect, create_engine

engine = create_engine('mysql+mysqlconnector://smartheaven:Smartheaven2024!@192.168.31.153:3306/smartheaven')
insp = inspect(engine)
cols = insp.get_columns('button_events')

print("button_events columns:")
for c in cols:
    nullable = "NULL" if c['nullable'] else "NOT NULL"
    default = f"DEFAULT {c['default']}" if c.get('default') else ""
    print(f"  {c['name']}: {c['type']} {nullable} {default}")
