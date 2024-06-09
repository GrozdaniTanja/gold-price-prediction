import pandas as pd
import json
import os
from evidently.test_suite import TestSuite
from evidently.test_preset import DataStabilityTestPreset, NoTargetPerformanceTestPreset
from evidently.tests import TestNumberOfColumnsWithMissingValues, TestNumberOfRowsWithMissingValues, \
    TestNumberOfConstantColumns, TestNumberOfDuplicatedRows, TestNumberOfDuplicatedColumns, TestColumnsType, \
    TestNumberOfDriftedColumns

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(ROOT_DIR, '..', '..', 'reports')

if __name__ == "__main__":
    tests = TestSuite(tests=[
        TestNumberOfColumnsWithMissingValues(),
        TestNumberOfRowsWithMissingValues(),
        TestNumberOfConstantColumns(),
        TestNumberOfDuplicatedRows(),
        TestNumberOfDuplicatedColumns(),
        TestColumnsType(),
        TestNumberOfDriftedColumns(),
        NoTargetPerformanceTestPreset(),
        DataStabilityTestPreset()
    ])

    current = pd.read_csv("data/current_data.csv")
    reference = pd.read_csv("data/reference_data.csv")

    tests.run(reference_data=reference, current_data=current)

    tests.save_html("reports/sites/stability_tests.html")

    test_results = tests.json()
    parsed_results = json.loads(test_results)

    output_file = os.path.join(
        REPORTS_DIR, "test_results.json")

    if os.path.exists(output_file) and os.stat(output_file).st_size != 0:
        with open(output_file, 'r') as f:
            results_array = json.load(f)
    else:
        results_array = []

    results_array.append(parsed_results)

    with open(output_file, 'w') as f:
        json.dump(results_array, f, indent=4)
