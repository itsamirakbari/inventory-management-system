CREATE DATABASE inventory_management_system;
USE inventory_management_system;

CREATE TABLE categories (
id INT PRIMARY KEY AUTO_INCREMENT,

name VARCHAR(100) UNIQUE NOT NULL,
description TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NULL
	ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE suppliers (
id INT PRIMARY KEY AUTO_INCREMENT,

company_name VARCHAR(150) UNIQUE NOT NULL,
contact_person VARCHAR(100),
email VARCHAR(255),
phone VARCHAR(30),
street VARCHAR(150),
house_number VARCHAR(20),
postal_code VARCHAR(20),
city VARCHAR(100),
country VARCHAR(100),
description TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NULL
	ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE products (
id INT PRIMARY KEY AUTO_INCREMENT,

name VARCHAR(150) NOT NULL,
sku VARCHAR(100) UNIQUE NOT NULL,
price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
is_active BOOLEAN NOT NULL DEFAULT TRUE,

category_id INT NOT NULL,
supplier_id INT NOT NULL,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NULL 
	ON UPDATE CURRENT_TIMESTAMP,

FOREIGN KEY (category_id) REFERENCES categories(id) ON UPDATE CASCADE ON DELETE RESTRICT,
FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE users (
id INT PRIMARY KEY AUTO_INCREMENT,

username VARCHAR(50) UNIQUE NOT NULL,
email VARCHAR(255) UNIQUE NOT NULL,
password_hash VARCHAR(255) NOT NULL,
role ENUM('admin', 'employee') NOT NULL DEFAULT 'employee',

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NULL
	ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE inventory_transactions (
id INT PRIMARY KEY AUTO_INCREMENT,

transaction_type ENUM('stock_in', 'stock_out', 'adjustment') NOT NULL,

product_id INT NOT NULL,
user_id INT NOT NULL,

quantity INT NOT NULL CHECK (quantity > 0),
note TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NULL
	ON UPDATE CURRENT_TIMESTAMP,
    
FOREIGN KEY (product_id) REFERENCES products(id) ON UPDATE CASCADE ON DELETE RESTRICT,
FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE RESTRICT
);


# Korrektor für tabelle inventory_transactions #

ALTER TABLE inventory_transactions
MODIFY COLUMN transaction_type ENUM(
    'stock_in',
    'stock_out',
    'adjustment_in',
    'adjustment_out'
) NOT NULL,
ADD COLUMN reason ENUM(
    'purchase',
    'sale',
    'return_in',
    'return_out',
    'damaged_goods',
    'lost_goods',
    'recount_correction',
    'manual_adjustment',
    'other'
) NOT NULL AFTER quantity,
ADD COLUMN transaction_reference VARCHAR(100) NOT NULL AFTER reason,
ADD CONSTRAINT chk_inventory_transactions_other_note
CHECK (
    reason <> 'other'
    OR (note IS NOT NULL AND TRIM(note) <> '')
);


CREATE TABLE customers (
id INT PRIMARY KEY AUTO_INCREMENT,

customer_name VARCHAR(150) NOT NULL,
contact_person VARCHAR(100),
email VARCHAR(255),
phone VARCHAR(30),
street VARCHAR(150) NOT NULL,
house_number VARCHAR(20) NOT NULL,
postal_code VARCHAR(20) NOT NULL,
city VARCHAR(100) NOT NULL,
country VARCHAR(100) NOT NULL,
description TEXT,
is_active BOOLEAN NOT NULL DEFAULT TRUE,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE invoices (
id INT PRIMARY KEY AUTO_INCREMENT,
invoice_number VARCHAR(50) UNIQUE NOT NULL,

customer_id INT NOT NULL,
user_id INT NOT NULL,

invoice_date DATE NOT NULL DEFAULT (CURRENT_DATE),
status ENUM('open', 'paid') NOT NULL DEFAULT 'open',
total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
note TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,

FOREIGN KEY (customer_id) REFERENCES customers(id) ON UPDATE CASCADE ON DELETE RESTRICT,
FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE RESTRICT
);


CREATE TABLE invoice_items (
id INT PRIMARY KEY AUTO_INCREMENT,

invoice_id INT NOT NULL,
product_id INT NOT NULL,

quantity INT NOT NULL CHECK (quantity > 0),
unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

UNIQUE (invoice_id, product_id),

FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON UPDATE CASCADE ON DELETE RESTRICT,
FOREIGN KEY (product_id) REFERENCES products(id) ON UPDATE CASCADE ON DELETE RESTRICT
);



































