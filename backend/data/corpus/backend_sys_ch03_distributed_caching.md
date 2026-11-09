# Backend Systems & Distributed Architecture Handbook
## Module 3: Distributed Systems, Caching, and Resiliency

### Caching Strategies and Invalidation
Caches reduce database load and network latency by retaining frequently accessed data in memory (Redis, Memcached):
- **Cache-Aside (Lazy Loading)**: Application inspects cache first. On miss, it queries database, populates cache, and returns response. Subsequent writes invalidate or delete the cached entry to prevent stale state.
- **Write-Through**: Application writes data directly to cache, which synchronously persists it to the datastore before acknowledging success.
- **Write-Behind (Write-Back)**: Writes are acknowledged immediately after memory insertion; an asynchronous worker flushes batched writes to disk later, introducing potential data loss risks during node crashes.
- **Cache Stampede (Thundering Herd)**: Occurs when a popular cached key expires, and thousands of concurrent requests simultaneously hit the database to recompute the value. Mitigations include Mutex locking on cache miss, Probabilistic Early Expiration (XFetch algorithm), or pre-emptive background refreshing.

### The CAP Theorem and Consistency Models
Eric Brewer's CAP Theorem proves that a distributed data store can guarantee at most two out of three properties under network partitioning:
- **Consistency (Linearizability)**: Every read receives the most recent write or an error.
- **Availability**: Every non-failing node returns a non-error response, without guarantee of latest data.
- **Partition Tolerance**: The system continues operating despite dropped or delayed network packets between nodes.
Because physical network partitions ($P$) are unavoidable in real networks, distributed systems must trade off between $C$ (favoring linearizable consistency and rejecting writes on split-brain, e.g., Raft/Paxos consensus systems like etcd, ZooKeeper) and $A$ (favoring high availability and eventual consistency, e.g., Amazon Dynamo, Apache Cassandra).

### Resiliency Patterns: Circuit Breakers, Rate Limiting & Idempotency
- **Circuit Breaker Pattern**: Wraps calls to external services. Tracks failure rates; when errors exceed a threshold, transitions from *Closed* to *Open* to immediately fail subsequent requests without overloading the downstream service. After a cooldown, enters *Half-Open* to probe recovery.
- **Rate Limiting**: Protects APIs from noisy neighbors or denial-of-service using algorithms like Token Bucket, Leaky Bucket, or Sliding Window Counter.
- **Idempotency**: Guarantees that performing the same operation multiple times yields the same system state as a single invocation. HTTP GET, PUT, and DELETE are idempotent by specification; POST endpoints achieve idempotency using client-supplied unique `Idempotency-Key` headers stored in Redis with atomic `SETNX`.
