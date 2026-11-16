
from sqlalchemy import inspect

from app.core.database import engine, Base
from app.models import CodeChunk


# Create database tables.
Base.metadata.create_all(bind=engine)

# Inspect the created table.
inspector = inspect(engine)

tables = inspector.get_table_names()

assert "code_chunks" in tables

columns = inspector.get_columns("code_chunks")

column_names = {
    column["name"] for column in columns
}

expected_columns = {
    "id",
    "chunk_id",
    "repository_path",
    "file_path",
    "language",
    "chunk_index",
    "start_line",
    "end_line",
    "content",
    "embedding",
    "embedding_model",
    "metadata",
    "created_at",
}

assert expected_columns.issubset(column_names)

print("CodeChunk database model test passed!")
print("Table:", "code_chunks")
print("Columns:", sorted(column_names))
