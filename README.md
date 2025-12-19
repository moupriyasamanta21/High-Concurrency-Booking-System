# 🎟️ High-Concurrency Railway Booking System

A robust simulation of a ticket booking engine designed to handle massive concurrent traffic while preventing **Double Booking** anomalies. This project demonstrates the implementation of **Optimistic Concurrency Control (OCC)** using Python and PostgreSQL.

---

## 🚀 The Challenge
In real-world scenarios (like **IRCTC** or **Ticketmaster**), thousands of users may click **"Book"** on the last available seat at the exact same millisecond.  
Without proper concurrency control, the database can suffer from **Lost Updates**, leading to more tickets being sold than available seats.

This project solves that problem using **Optimistic Locking** with a versioning mechanism.

---

## 🛠️ Tech Stack
- **Language:** Python 3.14 (Multi-threaded)
- **Database:** PostgreSQL
- **Library:** [`psycopg2`](https://pypi.org/project/psycopg2/)
- **Concurrency Strategy:** Optimistic Locking (Versioning)

---

## 🏗️ Project Architecture
The system is divided into three logical layers:

1. **Simulation Layer:**  
   A Python script spawning 100+ concurrent threads (users).

2. **Logic Layer:**  
   Implements a **Read-Verify-Write** cycle that detects data collisions.

3. **Data Layer:**  
   A PostgreSQL schema utilizing a monotonic `version` counter for row-level validation.

---

## 📂 Repository Structure
```text
High-Concurrency-Booking/
├── src/
│   └── booking_system.py    # Main simulation logic
├── sql/
│   └── schema.sql           # Database tables and initial data
├── docs/
│   └── concurrency_specs.md # Deep dive into 
|__ tests/
|   |__ output               # output of python
|   |__ databse_output       # state of database
locking logic
├── .gitignore               # Keeps the repo clean
└── README.md                # Project overview
```

---

## 🚥 How to Run

### ✅ 1. Prerequisites
Ensure you have:
- PostgreSQL installed and running
- Python environment ready

Install dependencies:
```bash
pip install psycopg2
```

---

### ✅ 2. Database Setup
Run the script in `sql/schema.sql` to create the database and tables:

```sql
-- Creates seats table with a version column
CREATE TABLE seats (
    seat_id SERIAL PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'available',
    version INT DEFAULT 0
);
```

Insert sample data:
```sql
INSERT INTO seats (status, version) VALUES ('available', 0);
```

---

### ✅ 3. Run the Simulation
Update the `DB_CONFIG` in `src/booking_system.py` with your database credentials, then run:

```bash
python src/booking_system.py
```

---

## 📊 Results & Analysis
The simulation provides a terminal report summarizing the efficiency of the concurrency control:

- **Success:** Transactions that successfully updated the version.
- **Collision:** Transactions rejected because the version changed during processing.
- **Taken:** Transactions that attempted to book a seat already finalized.

---

## 📄 Documentation
For a detailed explanation of:
- **Pessimistic vs. Optimistic Locking**
- **ACID compliance**
- **Concurrency strategies**

Refer to:  
`docs/concurrency_specs.md`

---

## ✅ Key Features
- Handles **100+ concurrent booking attempts** safely.
- Prevents **double booking** using **version-based optimistic locking**.
- Demonstrates **real-world concurrency control** in ticketing systems.

---

## 🔮 Future Enhancements
- Implement **retry logic** for failed transactions.
- Add **web interface** for booking simulation.
- Extend to **multiple seats and trains**.

---


