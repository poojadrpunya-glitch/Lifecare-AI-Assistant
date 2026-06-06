CREATE TABLE emergency_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(20),
    location TEXT,
    message TEXT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);