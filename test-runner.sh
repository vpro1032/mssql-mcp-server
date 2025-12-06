#!/bin/bash
set -e

echo "=========================================="
echo "MSSQL MCP Server - Automated Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}[${1}]${NC} ${3}"
}

# Step 1: Clean up any existing containers
print_status "CLEANUP" "$YELLOW" "Removing existing test containers..."
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true

# Step 2: Build the MCP server image
print_status "BUILD" "$YELLOW" "Building MCP server Docker image..."
docker build -t mssql-mcp-server:test . || {
    print_status "BUILD" "$RED" "Failed to build Docker image"
    exit 1
}

# Step 3: Start test environment
print_status "START" "$YELLOW" "Starting test environment (MSSQL + MCP Server)..."
docker-compose -f docker-compose.test.yml up -d

# Step 4: Wait for MSSQL to be ready
print_status "WAIT" "$YELLOW" "Waiting for MSSQL database to be ready..."
timeout=60
counter=0
until docker exec mssql-test-db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'Test1234!@#$' -Q "SELECT 1" > /dev/null 2>&1; do
    sleep 2
    counter=$((counter + 2))
    if [ $counter -ge $timeout ]; then
        print_status "WAIT" "$RED" "Timeout waiting for MSSQL database"
        docker-compose -f docker-compose.test.yml logs mssql-test
        docker-compose -f docker-compose.test.yml down -v
        exit 1
    fi
    echo -n "."
done
echo ""
print_status "READY" "$GREEN" "MSSQL database is ready"

# Step 5: Wait for MCP server to be ready
print_status "WAIT" "$YELLOW" "Waiting for MCP server to be ready..."
sleep 10

# Step 6: Run integration tests
print_status "TEST" "$YELLOW" "Running integration tests..."
python3 tests/integration/test_mcp_tools.py

TEST_EXIT_CODE=$?

# Step 7: Save logs
print_status "LOGS" "$YELLOW" "Saving container logs..."
docker-compose -f docker-compose.test.yml logs > test-logs.txt

# Step 8: Cleanup
print_status "CLEANUP" "$YELLOW" "Cleaning up test environment..."
docker-compose -f docker-compose.test.yml down -v

# Step 9: Report results
echo ""
echo "=========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_status "RESULT" "$GREEN" "All tests passed! ✓"
    echo "=========================================="
    exit 0
else
    print_status "RESULT" "$RED" "Some tests failed! ✗"
    echo "=========================================="
    echo "Check test-logs.txt for details"
    exit 1
fi
