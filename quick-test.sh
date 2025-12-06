#!/bin/bash
# Quick manual test script for AI tools

echo "Quick MCP Server Test"
echo "====================="

# Test 1: List databases
echo -e "\n[Test 1] Listing databases..."
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"mssql_list_databases","arguments":{}}}' | \
docker run -i --rm --network host \
  -e MSSQL_HOST=localhost \
  -e MSSQL_USER=sa \
  -e MSSQL_PASSWORD='Test1234!@#$' \
  mssql-mcp-server:test

# Test 2: List tables
echo -e "\n[Test 2] Listing tables..."
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"mssql_list_tables","arguments":{"database":"TestDB","schema":"test"}}}' | \
docker run -i --rm --network host \
  -e MSSQL_HOST=localhost \
  -e MSSQL_DATABASE=TestDB \
  -e MSSQL_USER=sa \
  -e MSSQL_PASSWORD='Test1234!@#$' \
  mssql-mcp-server:test

# Test 3: Query data
echo -e "\n[Test 3] Querying customer data..."
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"mssql_query","arguments":{"query":"SELECT TOP 3 * FROM test.Customers","database":"TestDB"}}}' | \
docker run -i --rm --network host \
  -e MSSQL_HOST=localhost \
  -e MSSQL_DATABASE=TestDB \
  -e MSSQL_USER=sa \
  -e MSSQL_PASSWORD='Test1234!@#$' \
  mssql-mcp-server:test

echo -e "\nDone!"
