-- Inventory Management System Pro
-- Final MySQL 8 schema: users, catalog, customers, invoices, and stock movements.

CREATE DATABASE IF NOT EXISTS inventory_management_system
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE inventory_management_system;

CREATE TABLE IF NOT EXISTS categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_categories_name UNIQUE (name)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS suppliers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100) NULL,
    email VARCHAR(255) NULL,
    phone VARCHAR(30) NULL,
    street VARCHAR(150) NULL,
    house_number VARCHAR(20) NULL,
    postal_code VARCHAR(20) NULL,
    city VARCHAR(100) NULL,
    country VARCHAR(100) NULL,
    description TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_suppliers_company_name UNIQUE (company_name)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'employee') NOT NULL DEFAULT 'employee',
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100) NULL,
    email VARCHAR(255) NULL,
    phone VARCHAR(30) NULL,
    street VARCHAR(150) NOT NULL,
    house_number VARCHAR(20) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    description TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    sku VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    category_id INT NOT NULL,
    supplier_id INT NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_products_sku UNIQUE (sku),
    CONSTRAINT chk_products_price CHECK (price >= 0),
    CONSTRAINT chk_products_stock_quantity CHECK (stock_quantity >= 0),
    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES categories (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_products_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS invoices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number VARCHAR(50) NOT NULL,
    customer_id INT NOT NULL,
    user_id INT NOT NULL,
    invoice_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    status ENUM('open', 'paid') NOT NULL DEFAULT 'open',
    total_amount DECIMAL(10, 2) NOT NULL,
    note TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_invoices_invoice_number UNIQUE (invoice_number),
    CONSTRAINT chk_invoices_total_amount CHECK (total_amount >= 0),
    CONSTRAINT fk_invoices_customer
        FOREIGN KEY (customer_id) REFERENCES customers (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_invoices_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS invoice_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_invoice_items_invoice_product UNIQUE (invoice_id, product_id),
    CONSTRAINT chk_invoice_items_quantity CHECK (quantity > 0),
    CONSTRAINT chk_invoice_items_unit_price CHECK (unit_price >= 0),
    CONSTRAINT fk_invoice_items_invoice
        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_invoice_items_product
        FOREIGN KEY (product_id) REFERENCES products (id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS inventory_transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_type ENUM(
        'stock_in',
        'stock_out',
        'adjustment_in',
        'adjustment_out'
    ) NOT NULL,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    quantity INT NOT NULL,
    reason ENUM(
        'purchase',
        'sale',
        'return_in',
        'return_out',
        'damaged_goods',
        'lost_goods',
        'recount_correction',
        'manual_adjustment',
        'other'
    ) NOT NULL,
    transaction_reference VARCHAR(100) NOT NULL,
    note TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_inventory_transactions_quantity CHECK (quantity > 0),
    CONSTRAINT chk_inventory_transactions_other_note CHECK (
        reason <> 'other'
        OR (note IS NOT NULL AND TRIM(note) <> '')
    ),
    CONSTRAINT fk_inventory_transactions_product
        FOREIGN KEY (product_id) REFERENCES products (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_inventory_transactions_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;
