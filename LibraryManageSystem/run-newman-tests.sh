#!/bin/bash

# Newman Test Runner Script for Library Management System
# This script runs automated API tests using Newman (Postman CLI)

set -e  # Exit on error

echo "=================================================="
echo "Library Management System - Newman Test Runner"
echo "=================================================="
echo ""

# Check if Newman is installed
if ! command -v newman &> /dev/null; then
    echo "❌ Error: Newman is not installed"
    echo "Please install Newman using: npm install -g newman"
    exit 1
fi

echo "✅ Newman is installed"
echo ""

# Check if Flask app is running
echo "Checking if Flask app is running on http://127.0.0.1:5000..."
if ! curl -s http://127.0.0.1:5000/api/books > /dev/null 2>&1; then
    echo "❌ Error: Flask app is not running"
    echo "Please start the Flask app first using:"
    echo "  cd LibraryManageSystem"
    echo "  python app_swagger.py"
    exit 1
fi

echo "✅ Flask app is running"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set collection path
COLLECTION_PATH="$SCRIPT_DIR/LibraryManagement.postman_collection.json"

# Check if collection file exists
if [ ! -f "$COLLECTION_PATH" ]; then
    echo "❌ Error: Postman collection not found at $COLLECTION_PATH"
    exit 1
fi

echo "✅ Postman collection found"
echo ""

# Run Newman tests
echo "=================================================="
echo "Running Newman Tests"
echo "=================================================="
echo ""

newman run "$COLLECTION_PATH" \
    --reporters cli,json,html \
    --reporter-json-export newman-results.json \
    --reporter-html-export newman-report.html \
    --color on \
    --timeout-request 10000 \
    --bail

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ All tests passed successfully!"
    echo "=================================================="
    echo ""
    echo "Test reports generated:"
    echo "  📄 JSON Report: newman-results.json"
    echo "  📄 HTML Report: newman-report.html"
    echo ""
    exit 0
else
    echo ""
    echo "=================================================="
    echo "❌ Some tests failed"
    echo "=================================================="
    echo ""
    echo "Check the reports for details:"
    echo "  📄 JSON Report: newman-results.json"
    echo "  📄 HTML Report: newman-report.html"
    echo ""
    exit 1
fi
