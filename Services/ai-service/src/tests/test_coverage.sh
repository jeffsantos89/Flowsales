#!/bin/bash

# Define directories and files
SRC_DIR="../src"
TEST_DIR="../tests"
COVERAGE_DIR="../coverage"
COVERAGE_REPORT="$COVERAGE_DIR/coverage_report.txt"

# Create coverage directory if it doesn't exist
mkdir -p $COVERAGE_DIR

# Run tests with coverage
echo "Running tests with coverage..."
pytest --cov=$SRC_DIR --cov-report=term-missing --cov-report=html:$COVERAGE_DIR/html --cov-report=xml:$COVERAGE_DIR/coverage.xml $TEST_DIR > $COVERAGE_REPORT

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "Tests passed successfully."
else
    echo "Some tests failed. Check the coverage report for details."
    exit 1
fi

# Display coverage summary
echo "Coverage summary:"
cat $COVERAGE_REPORT | grep -E "TOTAL|Coverage"

# Notify user of report locations
echo "HTML coverage report generated at: $COVERAGE_DIR/html/index.html"
echo "XML coverage report generated at: $COVERAGE_DIR/coverage.xml"
echo "Text coverage report generated at: $COVERAGE_REPORT"

exit 0