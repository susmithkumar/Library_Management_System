-- schema.sql

CREATE DATABASE IF NOT EXISTS library_management_system;
USE library_management_system;

CREATE TABLE IF NOT EXISTS user_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid VARCHAR(100) UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
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
    embedding JSON,
    isbn VARCHAR(50),
    image_url VARCHAR(255)
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
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (responsibility_id) REFERENCES responsibilities(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS book_issues (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        book_id INT,
        issue_date DATE,
        return_date DATE,
        FOREIGN KEY (user_id) REFERENCES user_table(id),
        FOREIGN KEY (book_id) REFERENCES add_book(id)
)

INSERT IGNORE INTO roles (id, name, description) VALUES 
(1, 'Admin', 'have all accesses'),
(2, 'user', 'can access to user profile'),
(3, 'libratioan123', 'limited acceseddf'),
(4, 'user456', 'have all accesses'),
(5, 'vinod', 'have all access');

INSERT IGNORE INTO responsibilities (id, name, description, path) VALUES
(1, 'Roles', 'where we control roles', '/roles'),
(2, 'Responsibilites', 'where we control responsibility', '/responsibility'),
(3, 'book', 'where we control book', '/books'),
(4, 'view users', 'where we control roleing', '/view_user'),
(5, 'add books', 'can add books', '/add_book'),
(6, 'user details', 'can see user infromation', '/view_user'),
(7, 'Dashboard', 'dashboard', '/dashboard'),
(8, 'Modify Users', 'limited acces', '/users'),
(9, 'room', 'have all access', '/');

INSERT IGNORE INTO roles_responsibilities (role_id, responsibility_id) VALUES
(1, 1), (2, 1), (4, 1), (5, 1), (1, 2), (3, 2), (1, 3), (2, 3),
(1, 4), (1, 5), (2, 5), (1, 6), (1, 7), (1, 8), (2, 9);


INSERT IGNORE INTO user_table (id, first_name, email, password, role, last_name, active, userid, address) VALUES
(1, 'susmith', 'susmith@gmail.com', '$2b$12$e.bzITCHpRCwQrevV.Dj3eksketl5c6iYAubSZCwn1l/axV6wtJYG', 1, NULL, 1, 'LB1', NULL),
(2, 'kishan', 'kishan@gmail.com', '$2b$12$e.bzITCHpRCwQrevV.Dj3eksketl5c6iYAubSZCwn1l/axV6wtJYG', 2, NULL, 1, 'LB2', NULL),
(3, 'karthik', 'karthik@gmail.com', '$2b$12$e.bzITCHpRCwQrevV.Dj3eksketl5c6iYAubSZCwn1l/axV6wtJYG', 2, NULL, 1, 'LB3', NULL),
(4, 'mohit', 'mohit@gmail.com', '$2b$12$afRTTpbTAn6NZGkToaGulOSXuyQFe1F9CEFm5JbZgcoT8Vij/CY6K', 2, NULL, 1, 'LB4', NULL),
(5, 'gowtham', 'gowtham@gmail.com', '$2b$12$/tVkDcIdReGQK31CIpOmSeLCqtrsgno.Q.vtSqpE3yswIFMQpVMlu', 2, NULL, 1, 'LB5', NULL),
(7, 'ruthwik1234', 'ruthwik@gmal.com', '$2b$12$l/9mhU.sYieTyqowMhOwKOnBZ6Khib13kz/.0MF30ryn4kyMp.yVq', 1, 'sonwregf', 1, 'LB7', '4400 McPherson avenue');