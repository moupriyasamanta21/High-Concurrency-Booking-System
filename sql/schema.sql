-- Create the seats table
CREATE TABLE seats (
    seat_id INT PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'AVAILABLE', -- 'AVAILABLE' or 'BOOKED'
    version INT DEFAULT 0                   -- Used for Optimistic Locking
);

-- Create the bookings table to track who bought what
CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY,
    seat_id INT REFERENCES seats(seat_id),
    user_id VARCHAR(50),
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert 10 sample seats

INSERT INTO seats (seat_id) SELECT generate_series(1, 10);

booking_db=# update seats
booking_db-# set status = 'BOOKED', version = version + 1
booking_db-# where seat_id = 1 and version = 0;

SELECT * FROM seats;
SELECT * FROM bookings;
