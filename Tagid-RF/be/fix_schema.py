import logging
from sqlalchemy import text, inspect
from app.services.database import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_schema():
    logger.info("Starting schema verification and fix...")
    
    inspector = inspect(engine)
    table_name = "rfid_tags"
    
    if not inspector.has_table(table_name):
        logger.error(f"Table {table_name} does not exist! Run init_db() first.")
        return

    existing_columns = [c["name"] for c in inspector.get_columns(table_name)]
    logger.info(f"Existing columns: {existing_columns}")

    # Define missing columns to check and adding logic
    # Column mapping: Name -> SQL Type & Constraints
    new_columns = {
        "is_paid": "BOOLEAN DEFAULT FALSE NOT NULL",
        "product_name": "VARCHAR(255)",
        "product_sku": "VARCHAR(50)",
        "price_cents": "INTEGER",
        "store_id": "INTEGER",
        "paid_at": "TIMESTAMP WITH TIME ZONE",
        "read_count": "INTEGER DEFAULT 1 NOT NULL",
        "user_memory": "TEXT",
        "pc": "VARCHAR(16)",
        "crc": "VARCHAR(16)",
        "frequency": "FLOAT",
        "metadata": "JSON"
    }




    with engine.connect() as conn:
        with conn.begin(): # Transaction
            for col, definition in new_columns.items():
                if col not in existing_columns:
                    logger.info(f"Adding missing column: {col}")
                    try:
                        sql = f'ALTER TABLE {table_name} ADD COLUMN "{col}" {definition}'
                        conn.execute(text(sql))
                        logger.info(f"Successfully added column {col}")
                    except Exception as e:
                        logger.error(f"Failed to add column {col}: {e}")
                else:
                    logger.info(f"Column {col} already exists.")

    logger.info("Schema fix complete.")

if __name__ == "__main__":
    fix_schema()
