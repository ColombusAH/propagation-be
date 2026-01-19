import re
import os

SCHEMA_PATH = "prisma/schema.prisma"
BACKUP_PATH = "prisma/schema.prisma.bak"

def clean_schema():
    if not os.path.exists(SCHEMA_PATH):
        print(f"Error: {SCHEMA_PATH} not found.")
        return

    # Read the file (forcing utf-8 to ensure we read it correctly first)
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Create backup
        with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Backup created at {BACKUP_PATH}")

        # Remove non-ascii characters but keep newlines and standard symbols
        # This regex matches any character that is NOT in the ASCII range (0-127)
        clean_content = re.sub(r'[^\x00-\x7F]+', '', content)

        with open(SCHEMA_PATH, 'w', encoding='utf-8') as f:
            f.write(clean_content)
            
        print("Successfully removed non-ASCII characters from schema.prisma")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    clean_schema()
