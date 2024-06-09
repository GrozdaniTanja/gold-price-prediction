import os
import json
import great_expectations as ge
import pandas as pd
from great_expectations.checkpoint.types.checkpoint_result import CheckpointResult
from datetime import datetime


def main():
    context = ge.get_context()
    result = None
    try:
        result: CheckpointResult = context.run_checkpoint(
            checkpoint_name="merge_checkpoint")

        if not result["success"]:
            print("[Validate]: Checkpoint validation failed!")
        else:
            print("[Validate]: Checkpoint validation successful!")

    except Exception as e:
        print("[Validate]: Checkpoint validation failed!")
        print(e)
        return

    # Prepare the validation report
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    validation_report = f"\n --- \n Date and Time: {current_datetime}\n\n"
    if result:
        validation_report += json.dumps(result.to_json_dict(), indent=4)

    # Ensure the reports directory exists
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    REPORTS_DIR = os.path.join(ROOT_DIR, '..', '..', 'reports')
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Save the validation report
    output_file = os.path.join(REPORTS_DIR, "validation_report.txt")
    with open(output_file, 'a', encoding="utf-8") as f:
        f.write(validation_report)

    # Verify file creation
    if os.path.exists(output_file):
        print(f"Validation report successfully saved to {output_file}")
    else:
        print(f"Failed to save validation report to {output_file}")

    # Save current data
    current_data = pd.read_csv("data/current_data.csv")
    reference_data_path = "data/reference_data.csv"
    current_data.to_csv(reference_data_path, index=False)


if __name__ == "__main__":
    main()
