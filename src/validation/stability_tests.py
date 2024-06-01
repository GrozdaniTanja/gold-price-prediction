import pandas as pd
from evidently.test_suite import TestSuite
from evidently.test_preset import DataStabilityTestPreset, NoTargetPerformanceTestPreset
from evidently.tests import TestNumberOfColumnsWithMissingValues, TestNumberOfRowsWithMissingValues, \
    TestNumberOfConstantColumns, TestNumberOfDuplicatedRows, TestNumberOfDuplicatedColumns, TestColumnsType, \
    TestNumberOfDriftedColumns

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
