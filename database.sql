CREATE DATABASE coffee_orders;
USE coffee_orders;

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    coffee_type VARCHAR(255),
    sugar_level VARCHAR(255),
    cup_size VARCHAR(255),
    price DECIMAL(10, 2),
    timestamp DATETIME
);


