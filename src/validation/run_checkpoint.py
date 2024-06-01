import os
import great_expectations as ge
import pandas as pd
from great_expectations.checkpoint.types.checkpoint_result import CheckpointResult


def main():
    context = ge.get_context()
    try:
        result: CheckpointResult = context.run_checkpoint(
            checkpoint_name="merge_checkpoint")

        if not result["success"]:
            print("[Validate]: Checkpoint validation failed!")

    except Exception as e:
        print("[Validate]: Checkpoint validation failed!")
        print(e)
        return

    print("[Validate]: Checkpoint validation successful!")

    current_data = pd.read_csv("data/current_data.csv")
    reference_data_path = "data/reference_data.csv"
    current_data.to_csv(reference_data_path, index=False)


if __name__ == "__main__":
    main()
