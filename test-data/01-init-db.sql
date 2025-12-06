-- Create test database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'TestDB')
BEGIN
    CREATE DATABASE TestDB;
END
GO

USE TestDB;
GO

-- Create test schema
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'test')
BEGIN
    EXEC('CREATE SCHEMA test');
END
GO

-- Create test tables
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Customers' AND schema_id = SCHEMA_ID('test'))
BEGIN
    CREATE TABLE test.Customers (
        CustomerID INT PRIMARY KEY IDENTITY(1,1),
        FirstName NVARCHAR(50) NOT NULL,
        LastName NVARCHAR(50) NOT NULL,
        Email NVARCHAR(100) UNIQUE,
        CreatedDate DATETIME DEFAULT GETDATE(),
        IsActive BIT DEFAULT 1
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Orders' AND schema_id = SCHEMA_ID('test'))
BEGIN
    CREATE TABLE test.Orders (
        OrderID INT PRIMARY KEY IDENTITY(1,1),
        CustomerID INT NOT NULL,
        OrderDate DATETIME DEFAULT GETDATE(),
        TotalAmount DECIMAL(10,2),
        Status NVARCHAR(20),
        FOREIGN KEY (CustomerID) REFERENCES test.Customers(CustomerID)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Products' AND schema_id = SCHEMA_ID('test'))
BEGIN
    CREATE TABLE test.Products (
        ProductID INT PRIMARY KEY IDENTITY(1,1),
        ProductName NVARCHAR(100) NOT NULL,
        Category NVARCHAR(50),
        Price DECIMAL(10,2),
        StockQuantity INT DEFAULT 0
    );
END
GO

-- Insert test data
-- Use checks to prevent duplicate data on multiple runs
IF NOT EXISTS (SELECT * FROM test.Customers)
BEGIN
    INSERT INTO test.Customers (FirstName, LastName, Email) VALUES
    ('John', 'Doe', 'john.doe@example.com'),
    ('Jane', 'Smith', 'jane.smith@example.com'),
    ('Bob', 'Johnson', 'bob.johnson@example.com'),
    ('Alice', 'Williams', 'alice.williams@example.com'),
    ('Charlie', 'Brown', 'charlie.brown@example.com');
END

IF NOT EXISTS (SELECT * FROM test.Products)
BEGIN
    INSERT INTO test.Products (ProductName, Category, Price, StockQuantity) VALUES
    ('Laptop', 'Electronics', 999.99, 50),
    ('Mouse', 'Electronics', 29.99, 200),
    ('Keyboard', 'Electronics', 79.99, 150),
    ('Monitor', 'Electronics', 299.99, 75),
    ('Desk Chair', 'Furniture', 199.99, 30);
END

IF NOT EXISTS (SELECT * FROM test.Orders)
BEGIN
    INSERT INTO test.Orders (CustomerID, OrderDate, TotalAmount, Status) VALUES
    (1, '2024-01-15', 1299.97, 'Completed'),
    (2, '2024-01-16', 999.99, 'Completed'),
    (3, '2024-01-17', 329.98, 'Pending'),
    (1, '2024-01-18', 79.99, 'Completed'),
    (4, '2024-01-19', 499.98, 'Shipped');
END
GO

-- Create a test stored procedure
CREATE OR ALTER PROCEDURE test.GetCustomerOrders
    @CustomerID INT
AS
BEGIN
    SELECT 
        o.OrderID,
        o.OrderDate,
        o.TotalAmount,
        o.Status
    FROM test.Orders o
    WHERE o.CustomerID = @CustomerID
    ORDER BY o.OrderDate DESC;
END
GO

-- Create a test view
CREATE OR ALTER VIEW test.vw_CustomerOrderSummary AS
SELECT 
    c.CustomerID,
    c.FirstName,
    c.LastName,
    COUNT(o.OrderID) as TotalOrders,
    ISNULL(SUM(o.TotalAmount), 0) as TotalSpent
FROM test.Customers c
LEFT JOIN test.Orders o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName;
GO
