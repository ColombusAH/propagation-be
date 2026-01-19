import os

schema_path = r'c:\Users\eliran_ha\Documents\Eliran\propagation-be\Tagid-RF\be\prisma\schema.prisma'

def fix_schema():
    with open(schema_path, 'rb') as f:
        content = f.read()
    
    # Try to decode
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = content.decode('utf-16')
        except UnicodeDecodeError:
            text = content.decode('latin-1')
    
    # Remove BOM if present
    text = text.lstrip('\ufeff')
    
    # Basic structural check
    lines = text.splitlines()
    print(f"Total lines: {len(lines)}")
    
    # Write back as clean UTF-8
    with open(schema_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    
    print("Schema file rewritten as UTF-8.")

if __name__ == "__main__":
    fix_schema()
