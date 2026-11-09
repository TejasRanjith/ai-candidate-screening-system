# Backend Systems & Distributed Architecture Handbook
## Module 1: Concurrency, Asynchronous I/O, and Threading

### Concurrency Models and Execution Mechanics
Modern backend engineering demands high-throughput, low-latency concurrent request processing. Two primary paradigms govern concurrent systems:
1. **Thread-Based Concurrency**: OS threads execute independently. In multi-threaded runtimes, shared memory state requires synchronization primitives (Mutexes, Read-Write Locks, Semaphores, Condition Variables) to prevent race conditions and deadlocks. In CPython, the Global Interpreter Lock (GIL) prevents concurrent native execution of Python bytecode across OS threads, rendering pure CPU-bound multi-threading ineffective without multi-processing or native extensions.
2. **Event-Driven Asynchronous I/O**: Operating system multiplexers (`epoll` on Linux, `kqueue` on macOS/BSD, `IOCP` on Windows) allow a single thread running an Event Loop (e.g., Python `asyncio`, Node.js `libuv`) to monitor thousands of non-blocking socket descriptors simultaneously. Tasks yield control cooperatively at `await` boundaries when waiting for network or disk I/O, eliminating thread context-switching overhead and stack memory footprint.

Common pitfalls in asynchronous systems include blocking the event loop with synchronous CPU-heavy routines or synchronous disk operations, which stalls all concurrent tasks scheduled on that worker.

### Thread Safety, Locks, and Deadlocks
A race condition emerges when multiple concurrent execution paths access and modify shared state without synchronization, yielding non-deterministic outputs.
- **Deadlock Conditions (Coffman Conditions)**: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. Mitigations include strict hierarchical lock ordering, lock timeouts, and optimistic lock-free primitives (Compare-And-Swap / CAS).
- **Thread Pools**: For blocking I/O or CPU operations within an async runtime, work is offloaded to a bounded worker thread pool (`ThreadPoolExecutor`), isolating the primary event loop from blocking stalls.
