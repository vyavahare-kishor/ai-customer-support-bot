from routers import documents, support
from fastapi import FastAPI
from models.document import Document
from sqlalchemy import text
from database import Base, engine
from dotenv import load_dotenv
load_dotenv()


# Explicitly import every model — never rely on __init__.py for this


# Ensure vector extension exists before create_all
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

# Now create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Customer Support Bot")

app.include_router(documents.router)
app.include_router(support.router)


@app.get("/health")
def health():
    return {"status": "ok"}
