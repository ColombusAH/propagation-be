import json
import sys


def extract_coverage(json_file, target_files):
    try:
        with open(json_file, "r") as f:
            data = json.load(f)

        files_data = data.get("files", {})
        results = {}

        for target in target_files:
            # Try to find the target in the keys (handling backslashes)
            match = None
            for key in files_data.keys():
                if target.replace("/", "\\") in key or target.replace("\\", "/") in key:
                    match = key
                    break

            if match:
                summary = files_data[match].get("summary", {})
                results[target] = {
                    "percent": summary.get("percent_covered_display", "0.00"),
                    "missing": files_data[match].get("missing_lines", []),
                }
            else:
                results[target] = "Not found"

        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    extract_coverage(
        "coverage.json",
        [
            "app/services/rfid_reader.py",
            "app/services/tranzila_provider.py",
            "app/services/tag_listener_service.py",
            "app/routers/tags.py",
        ],
    )
