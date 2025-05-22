# Hive Optimizations

Hive optimizations can significantly improve query performance by structuring data efficiently and optimizing query execution. These optimizations are categorized into two main levels: table structure and query execution.

## 1. Table Structure Level
- **Partitioning**:
  - Divides large datasets into smaller, manageable segments based on column values (e.g., date, region).
  - Improves query performance by allowing Hive to scan only relevant partitions instead of the entire dataset.
- **Bucketing**:
  - Distributes data into a fixed number of buckets using a hash function applied to a specified column.
  - Enhances efficiency in data sampling and join operations by grouping related data together.

## 2. Query Level Optimization
- **Join Optimizations**:
  - Joins are resource-intensive operations that often involve data shuffling across nodes.
  - **Goal**: Minimize the number of join operations where possible to reduce computational cost and improve performance.

---

# Broadcast Join in Spark

Broadcast joins are a type of join optimization in Spark that leverage the distribution of data to improve efficiency. They are particularly useful when working with tables of differing sizes.

## 1. Map-Side Join
- **Overview**:
  - Applicable when one table is small enough to fit into memory.
  - The small table is broadcasted to all nodes in the cluster.
  - Each node holds the entire small table and a portion of the large table, performing the join locally during the map phase.
- **Key Feature**: No reduce phase is required, making it faster than traditional joins.
- **Join Scenarios**:
  - **Left Table (Small) & Right Table (Large)**:
    - Inner Join: Possible
    - Left Outer Join: Not Possible
    - Right Outer Join: Possible
    - Full Outer Join: Not Possible
  - **Left Table (Large) & Right Table (Small)**:
    - Inner Join: Possible
    - Left Outer Join: Possible
    - Right Outer Join: Not Possible
    - Full Outer Join: Not Possible

## 2. Bucket Map Join
- **Overview**:
  - Used when both tables are large and cannot fit into memory entirely.
  - Data is bucketed based on the join column, and only one bucket is loaded into memory at a time.
- **Optimization Constraints**:
  - Both tables must be bucketed on the join column.
  - The number of buckets in one table must be an integral multiple of the number of buckets in the other (e.g., 2 buckets can join with 2, 4, 6, etc.).
- **Advantage**:
  - Reduces memory usage compared to loading an entire table, as only a single bucket is processed at a time.

---

# Join Types

Hive and Spark support various join types tailored to different scenarios, particularly when optimizing for large datasets.

1. **Map-Side Join**:
   - Involves one small table and one large table.
   - The small table is broadcasted for efficient joining during the map phase.

2. **Bucket Map Join**:
   - Involves two large tables.
   - **Conditions**:
     - Both tables must be bucketed on the join column.
     - The number of buckets in one table must be an integral multiple of the other.

3. **Sort Merge Bucket Join (SMB)**:
   - Involves two large tables.
   - **Conditions**:
     - Both tables must be bucketed on the join column.
     - The number of buckets in both tables must be identical.
     - Both tables must be sorted on the join column.
   - **Example**:
     ```
     Table 1        Table 2
     4 Buckets      4 Buckets
     B1             B1
     B2             B2
     B3             B3
     B4             B4
     ```

---

# Hadoop Commands

Hadoop commands are essential for managing data in the Hadoop Distributed File System (HDFS). Below are some commonly used commands:

- **List Directory**:
  ```bash
  hadoop fs -ls /user/itv017499/hive_datasets
  ```
  - Displays the contents of the specified directory.

- **Remove Directory**:
  ```bash
  hadoop fs -rm -R /user/itv017499/hive_datasets
  ```
  - Deletes the specified directory and all its contents recursively.

- **Create Directories**:
  ```bash
  hadoop fs -mkdir /user/itv017499/hive_datasets/orders
  hadoop fs -mkdir /user/itv017499/hive_datasets/customers
  ```
  - Creates new directories in HDFS to store data files.

---

# Creating External Tables in Hive

External tables in Hive allow data to be queried without moving it into Hive’s warehouse directory. Below are examples of creating external tables for `customers` and `orders`.

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS customers_external(
    customer_id INT,
    customer_fname STRING, 
    customer_lname STRING, 
    username STRING,
    password STRING,
    address STRING,
    city STRING,
    state STRING, 
    pincode INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/itv017499/hive_datasets/customers/';

CREATE EXTERNAL TABLE IF NOT EXISTS orders_external(
    order_id INT,
    order_date STRING,
    customer_id INT,
    order_status STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/itv017499/hive_datasets/orders/';
```

- **Use Database**:
  ```sql
  USE trendytech_101;
  SHOW TABLES;
  ```
  - Switches to the specified database and lists all tables.

- **Example Join Query**:
  ```sql
  SELECT * FROM orders_external o 
  JOIN customers_external c
  ON o.customer_id = c.customer_id
  LIMIT 5;
  ```
  - Performs a join between `orders_external` and `customers_external` tables, limiting the output to 5 rows.
  - **Note**: This query triggers a MapReduce job, likely a map-side join with mappers and no reducers.

---

# Setting Properties in Hive

Hive properties can be configured to control how queries are executed.

- **Enable Map-Side Joins**:
  ```sql
  SET hive.auto.convert.join = True;
  ```
  - Automatically converts all eligible joins to map-side joins for better performance.

- **Disable Map-Side Joins**:
  ```sql
  SET hive.auto.convert.join = False;
  ```
  - Forces joins to use reducers, which may be necessary for certain scenarios.

- **Query Execution Observation**:
  - With `hive.auto.convert.join = True`, the example join query uses 2 mappers and 1 reducer.

---

# Explain Query Plan

To understand how Hive executes a query, use the `EXPLAIN` command:

```sql
EXPLAIN EXTENDED SELECT * FROM orders_external o 
JOIN customers_external c
ON o.customer_id = c.customer_id
LIMIT 5;
```

- Provides a detailed execution plan, including stages, operations, and resource usage.

---

# How Map-Side Join Works Internally

A map-side join is an efficient join mechanism that avoids the reduce phase. Here’s how it operates internally:

1. **Hash Map Creation**:
   - A local process creates a hash map from the small table before the MapReduce job begins.
2. **Distribution**:
   - The hash map is stored in the distributed file system (DFS) and broadcasted to all nodes.
3. **Local Storage**:
   - Each node stores the hash map in its local disk (distributed cache).
4. **Memory Loading**:
   - The hash map is loaded into memory on each node.
5. **Map Phase Execution**:
   - The MapReduce job starts, using the in-memory hash table to perform the join during the map phase.
