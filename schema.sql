-- schema.sql

CREATE DATABASE IF NOT EXISTS library_management_system;
USE library_management_system;

CREATE TABLE IF NOT EXISTS user_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid VARCHAR(100) UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    role INT,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS add_book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    rack VARCHAR(50),
    quantity INT,
    isbn VARCHAR(50)  
);

CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS responsibilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    path VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS roles_responsibilities (
    role_id INT,
    responsibility_id INT,
    PRIMARY KEY (role_id, responsibility_id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (responsibility_id) REFERENCES responsibilities(id)
);

CREATE TABLE IF NOT EXISTS book_issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    issue_date DATE,
    return_date DATE,
    is_returned BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES user_table(id),
    FOREIGN KEY (book_id) REFERENCES add_book(id)
)