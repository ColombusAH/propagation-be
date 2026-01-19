import os

schema_path = r'c:\Users\eliran_ha\Documents\Eliran\propagation-be\Tagid-RF\be\prisma\schema.prisma'

def sanitize_schema():
    # Read with multiple encodings to find the right one
    content = None
    for enc in ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']:
        try:
            with open(schema_path, 'r', encoding=enc) as f:
                content = f.read()
            print(f"Successfully read with {enc}")
            break
        except Exception:
            continue
    
    if not content:
        print("Failed to read schema with any encoding.")
        return

    # Basic structural sanitization
    # Ensure no weird characters, normalize line endings
    clean_content = content.replace('\r\n', '\n').lstrip('\ufeff')
    
    # Check for duplicate model names (case sensitive in Prisma)
    models = []
    for line in clean_content.splitlines():
        if line.strip().startswith('model '):
            model_name = line.strip().split()[1].split('{')[0].strip()
            models.append(model_name)
    
    duplicates = [m for m in models if models.count(m) > 1]
    if duplicates:
        print(f"WARNING: Duplicate models found: {set(duplicates)}")
    
    # Write back as clean UTF-8
    with open(schema_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(clean_content)
    
    print("Schema sanitized and written as UTF-8.")

if __name__ == "__main__":
    sanitize_schema()
