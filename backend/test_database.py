
from sqlalchemy import text

from app.core.database import engine, SessionLocal


# Test database connection.
try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT version()")
        )

        print("PostgreSQL connected successfully!")
        print(result.scalar())

        # Verify pgvector extension.
        extension = connection.execute(
            text("""
                SELECT extname
                FROM pg_extension
                WHERE extname = 'vector'
            """)
        ).scalar()

        assert extension == "vector"

        print("pgvector extension verified!")

    # Test SQLAlchemy session creation.
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        print("SQLAlchemy session test passed!")
    finally:
        db.close()

except Exception as exc:
    print("Database connection failed!")
    print(repr(exc))
    raise
