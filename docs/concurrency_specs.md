# 📑 Concurrency Control Specifications: High-Concurrency Booking System

This document provides a technical deep-dive into the architectural decisions and concurrency control mechanisms implemented in this project. It focuses on maintaining **Data Integrity** and **Consistency** (ACID properties) under heavy multi-threaded loads.

---

## 1. The Core Challenge: Race Conditions
In a high-traffic environment, "Race Conditions" occur when multiple threads attempt to access and modify the same data simultaneously. Without control, this leads to the **Lost Update Anomaly**, where a seat appears available to multiple users, resulting in "Double Booking."

### Simulation Environment:
* **Database:** PostgreSQL
* **Isolation Level:** Read Committed (Default).
* **Load Profile:** 100+ concurrent threads competing for a limited 10-row resource block.



---

## 2. Concurrency Strategies: Pessimistic vs. Optimistic

This project demonstrates the transition from traditional locking to high-scale versioning logic.

| Feature | Pessimistic Locking | Optimistic Concurrency Control (OCC) |
| :--- | :--- | :--- |
| **Philosophy** | "Prevention is better than cure." | "Conflict is rare; handle it if it happens." |
| **Mechanism** | Database Row Locks (`SELECT ... FOR UPDATE`). | Application-level Version Checks (`version`). |
| **User Experience** | Users must **wait** in a queue for the lock. | Users **succeed** or **fail** immediately. |
| **Performance** | High latency due to lock contention. | High throughput; zero physical locking. |



---

## 3. Implementation: The Beauty of Optimistic Logic
The final implementation utilizes **Optimistic Concurrency Control (OCC)**. This strategy is considered "beautiful" because it avoids physical database locks, allowing the database to scale horizontally while the application handles conflicts.

### The "Read-Verify-Write" Cycle:

1. **The Read Phase:** The application fetches the `status` and the current `version` of a seat without placing any locks.
   ```sql
   SELECT status, version FROM seats WHERE seat_id = %s;


## 2. The Verify & Write Phase (Atomic Update)
The core of our concurrency logic relies on an atomic update strategy. The update only executes if the version in the database is identical to the version seen during the initial **Read** phase. If a collision occurs (meaning another user updated the seat first), the `WHERE` clause fails to find a matching row, preventing the update.


 ## 3. Logical Verification:
The system validates the success of the update by checking the database response directly. Because the `WHERE` clause includes a version check, the result of the operation tells us if a collision occurred:

* **✅ Success:** If `cursor.rowcount > 0`, it indicates the version matched perfectly. The database has atomically incremented the version, effectively invalidating any other pending updates that were relying on the previous version number.
* **🔄 Collision:** If `cursor.rowcount == 0`, it means another concurrent user modified the row in the milliseconds between our **Read** and **Write** phases. The system detects this version mismatch immediately and triggers a **Rollback** to protect data integrity.


## 2. Database & DBMS Specifications

The schema is specifically optimized for high-performance **Row-Level Concurrency**.

### Physical Schema Design
| Column | Type | Purpose |
| :--- | :--- | :--- |
| **seat_id** | `INT` | Primary Key (Utilizes Clustered Index for $O(1)$ access). |
| **status** | `VARCHAR` | Current resource state (`AVAILABLE` or `BOOKED`). |
| **version** | `INT` | **Monotonic Counter** used for state validation. |



### ACID Implementation

* **Atomicity:** All operations (updating the seat and inserting the booking record) are wrapped in a single transaction block. If the version check fails, the associated booking record is never inserted, ensuring an "all or nothing" result.
* **Consistency:** The versioning logic ensures the system moves from one valid state to another, preventing invalid $N \rightarrow N$ state transitions.
* **Isolation:** By using the `version` as a predicate in the `UPDATE` statement, we handle isolation at the engine level without blocking concurrent reads.
* **Durability:** Ensured by PostgreSQL's **Write-Ahead Logging (WAL)**, which logs all changes to persistent storage to protect data against system crashes.



---

## 3. Simulation Analysis (100 Users / 10 Seats)

By running the high-concurrency simulation script, the system effectively manages three distinct states to maintain 100% data accuracy:

* **✅ SUCCESS:** The thread was the fastest to update a specific `seat_id` at its specific `version`.
* **🔄 COLLISION:** The thread attempted an update, but the version had already changed. Data integrity was preserved via the **Optimistic Concurrency Control (OCC)** guard.
* **❌ TAKEN:** The thread performed a Read and correctly identified the seat as already occupied by a previously successful transaction.
