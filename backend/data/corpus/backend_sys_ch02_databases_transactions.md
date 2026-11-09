# Backend Systems & Distributed Architecture Handbook
## Module 2: Database Storage, Indexing, and Transactions

### Storage Engines: B-Trees vs LSM-Trees
Relational and NoSQL databases employ specialized on-disk storage structures:
- **B+ Trees**: Balanced n-ary search trees optimized for block storage. Leaf nodes are sequentially linked for efficient range scans, while internal nodes route lookups in $O(\log N)$ disk page reads. B+ trees provide fast read performance and predictable point queries, but random writes require in-place page rewrites and write amplification.
- **Log-Structured Merge-Trees (LSM-Trees)**: Used in write-heavy systems (RocksDB, Cassandra). Incoming writes append sequentially to an in-memory sorted buffer (`MemTable`) and a sequential Write-Ahead Log (WAL) for durability. When full, MemTables are flushed to disk as immutable Sorted String Tables (SSTables). Background compaction merges sorted runs and purges deleted tombstones. Read amplification is mitigated using in-memory Bloom Filters.

### ACID Properties and Transaction Isolation Levels
ACID guarantees ensure data integrity across concurrent database transactions:
- **Atomicity**: All operations in a transaction succeed, or the entire transaction is rolled back.
- **Consistency**: The database transitions from one valid state satisfying all schema constraints to another.
- **Isolation**: Concurrent transactions execute without exposing intermediate uncommitted changes to one another.
- **Durability**: Committed transactions persist across crashes via the Write-Ahead Log (WAL).

ANSI SQL defines four isolation levels addressing specific concurrency phenomena:
1. **Read Uncommitted**: Susceptible to *Dirty Reads* (reading uncommitted data rolled back later).
2. **Read Committed**: Eliminates dirty reads; each query sees only committed data. Still susceptible to *Non-Repeatable Reads* (re-reading a row returns different values modified by a concurrent committed transaction).
3. **Repeatable Read**: Ensures queries within the same transaction see a consistent snapshot (implemented via Multi-Version Concurrency Control / MVCC). Susceptible to *Phantom Reads* (new rows inserted by concurrent transactions matching a range predicate).
4. **Serializable**: The strictest level, guaranteeing that the outcome of concurrent execution is equivalent to some serial ordering, enforced via two-phase locking (2PL) or Serializable Snapshot Isolation (SSI).
