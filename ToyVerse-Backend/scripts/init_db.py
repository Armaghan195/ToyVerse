
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base, engine
from app.models import User, Admin, Customer, Product, CartItem, Order, Review
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_if_not_exists():

    try:

        server = settings.db_server
        master_connection_string = (
            f"DRIVER={{{settings.db_driver}}};"
            f"SERVER={server};"
            f"DATABASE=master;"
            f"Trusted_Connection=yes"
        )

        from urllib.parse import quote_plus
        master_url = f"mssql+pyodbc:///?odbc_connect={quote_plus(master_connection_string)}"

        master_engine = create_engine(master_url, echo=False)

        with master_engine.connect() as conn:

            conn = conn.execution_options(isolation_level="AUTOCOMMIT")

            result = conn.execute(
                text(f"SELECT database_id FROM sys.databases WHERE name = '{settings.db_name}'")
            )

            if result.fetchone() is None:

                logger.info(f"Creating database {settings.db_name}...")
                conn.execute(text(f"CREATE DATABASE {settings.db_name}"))
                logger.info(f"Database {settings.db_name} created successfully")
            else:
                logger.info(f"Database {settings.db_name} already exists")

        master_engine.dispose()

    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise

def create_tables():

    try:
        logger.info("Creating database tables...")

        Base.metadata.create_all(bind=engine)

        logger.info("Database tables created successfully:")
        for table in Base.metadata.sorted_tables:
            logger.info(f"  - {table.name}")

    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

def verify_tables():

    try:
        logger.info("Verifying tables...")

        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = :db_name"
            ), {"db_name": settings.db_name})

            tables = [row[0] for row in result]

        logger.info(f"Found {len(tables)} tables in database:")
        for table in tables:
            logger.info(f"  - {table}")

        expected_tables = ['users', 'products', 'cart_items', 'orders', 'reviews']
        missing_tables = [t for t in expected_tables if t not in tables]

        if missing_tables:
            logger.warning(f"Missing tables: {missing_tables}")
        else:
            logger.info("All expected tables are present")

    except Exception as e:
        logger.error(f"Error verifying tables: {e}")

def main():

    try:
        logger.info("=" * 60)
        logger.info("ToyVerse Database Initialization")
        logger.info("=" * 60)

        logger.info("\nStep 1: Creating database...")
        create_database_if_not_exists()

        logger.info("\nStep 2: Creating tables...")
        create_tables()

        logger.info("\nStep 3: Verifying tables...")
        verify_tables()

        logger.info("\n" + "=" * 60)
        logger.info("Database initialization completed successfully!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("  1. Run: python scripts/seed_data.py (to add initial data)")
        logger.info("  2. Run: python -m app.main (to start the API server)")

    except Exception as e:
        logger.error(f"\n{'=' * 60}")
        logger.error("Database initialization FAILED!")
        logger.error(f"{'=' * 60}")
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
