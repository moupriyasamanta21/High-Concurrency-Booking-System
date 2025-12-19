import psycopg2
import threading
import time
import random

# Database connection configuration
DB_CONFIG = {
    "dbname": "booking_db",
    "user": "postgres",
    "password": "Mou@48503", # Replace with your real password
    "host": "localhost",
    "port": "5432"
}

# Global counters for the final report
stats = {
    "success": 0,
    "collision": 0,
    "already_taken": 0
}
stats_lock = threading.Lock()

def book_seat_optimistic(user_id):
    # Each user picks a random seat between 1 and 10
    seat_id = random.randint(1, 10)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. READ: Get the current status and version (NO LOCKING)
        cursor.execute("SELECT status, version FROM seats WHERE seat_id = %s", (seat_id,))
        result = cursor.fetchone()

        if result and result[0] == 'AVAILABLE':
            current_version = result[1]
            
            # Artificial delay to mimic network latency and force collisions
            time.sleep(random.uniform(0.05, 0.2)) 

            # 2. WRITE: Only update if the version hasn't changed since we read it
            cursor.execute("""
                UPDATE seats 
                SET status = 'BOOKED', version = version + 1 
                WHERE seat_id = %s AND version = %s
            """, (seat_id, current_version))

            # 3. VERIFY: Check if the update actually happened
            if cursor.rowcount > 0:
                cursor.execute("INSERT INTO bookings (seat_id, user_id) VALUES (%s, %s)", (seat_id, user_id))
                conn.commit()
                print(f"✅ SUCCESS: {user_id} booked Seat {seat_id} (Ver {current_version})")
                with stats_lock: stats["success"] += 1
            else:
                # This is the 'Optimistic' part: we detected a concurrent change!
                conn.rollback()
                print(f"🔄 COLLISION: {user_id} failed. Seat {seat_id} was modified by someone else!")
                with stats_lock: stats["collision"] += 1
        else:
            print(f"❌ TAKEN: {user_id} found Seat {seat_id} already occupied")
            with stats_lock: stats["already_taken"] += 1

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ ERROR for {user_id}: {e}")

# --- Simulation Execution ---
threads = []
print("🚀 Starting High-Concurrency Optimistic Simulation (100 Users, 10 Seats)...")
start_time = time.time()

for i in range(100):
    t = threading.Thread(target=book_seat_optimistic, args=(f"User_{i:02d}",))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

end_time = time.time()

# --- Final Report ---
print("\n" + "="*30)
print("🏁 SIMULATION COMPLETE")
print(f"Total Time: {end_time - start_time:.2f} seconds")
print(f"✅ Successful Bookings: {stats['success']}")
print(f"🔄 Optimistic Collisions: {stats['collision']}")
print(f"❌ Already Taken: {stats['already_taken']}")
print("="*30)