from sqlalchemy import inspect, text
from models.document import Document  # explicit import
from database import Base, engine
from dotenv import load_dotenv
load_dotenv()


print("Tables known to Base:", Base.metadata.tables.keys())

# Create extension first
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()
    print("vector extension ready ✅")

# Create tables
Base.metadata.create_all(bind=engine)
print("create_all done ✅")

# Verify
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables in DB:", tables)
