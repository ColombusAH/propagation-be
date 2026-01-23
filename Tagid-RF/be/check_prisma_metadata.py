import inspect

from prisma.models import Business


def check_business_fields():
    print("In-memory Business model fields:")
    # Check annotations/fields
    fields = (
        Business.__fields__.keys() if hasattr(Business, "__fields__") else "Unknown"
    )
    print(f"Fields: {fields}")

    if "slug" in fields:
        print("SUCCESS: 'slug' found in Business model.")
    else:
        print("FAILURE: 'slug' NOT found in Business model.")


if __name__ == "__main__":
    check_business_fields()
