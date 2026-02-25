CREATE DATABASE bank_db;
USE bank_db;
CREATE TABLE users(
		u_id INT AUTO_INCREMENT PRIMARY KEY,
        u_name VARCHAR(100),
        balance FLOAT DEFAULT '1000',
        security_key VARCHAR(100),
        email VARCHAR(100) unique,
        aadhar_no VARCHAR(20) unique,
        mobile_no VARCHAR(20),
        dob date,
        occupation VARCHAR(100),
        u_address VARCHAR(100),
        aadhar_doc VARCHAR(300),
        profile_pic VARCHAR(300),
        pancard_doc VARCHAR(300),
        pass VARCHAR(300),
        created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP())
	);
ALTER TABLE users auto_increment=234001;

INSERT INTO users(u_name,security_key,email,aadhar_no,mobile_no,dob,occupation,u_address,pass)
VALUES('admin','1234','admin123@gmail.com','268817428992','7010113069','2005-06-07','ADMIN','Tirunelveli Town','admin123');

SELECT * FROM users;


CREATE TABLE transactions(
	t_id INT AUTO_INCREMENT PRIMARY KEY,
    tu_id INT,
    amount_role ENUM('Deposit','Withdraw','Loan'),
    amount float,
    transactioned_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP()),
    t_date DATE DEFAULT (CURRENT_DATE()),
    amount_status ENUM('Deposited','Withdrawn','Loan Received','EMI Paid','Not Set'),
    FOREIGN KEY(tu_id) REFERENCES users(u_id)
	);
ALTER table transactions AUTO_INCREMENT=560001;

SELECT * FROM transactions;


CREATE TABLE loans(
	l_id INT AUTO_INCREMENT PRIMARY KEY,
    lu_id INT,
    l_name VARCHAR(100),
    interest INT,
    time_tenure INT,
    l_amount FLOAT,
    l_details VARCHAR(300),
    l_doc_details VARCHAR(300),
    l_doc1 VARCHAR(300),
    l_doc2 VARCHAR(300),
	l_status ENUM('Not Active','Active','Completed') DEFAULT 'Not Active',
    FOREIGN KEY(lu_id) REFERENCES users(u_id)
    );
ALTER TABLE loans AUTO_INCREMENT=650001;

SELECT * FROM loans;


CREATE TABLE emi_schedule(
	emi_id INT AUTO_INCREMENT PRIMARY KEY,
    lemi_id INT,
    uemi_id INT,
    emi_amount FLOAT,
    due_date DATE,
    fine FLOAT DEFAULT '0',
    paid_date DATE,
    emi_status ENUM ('Not Paid','Paid') DEFAULT 'Not Paid',
    FOREIGN KEY(lemi_id) REFERENCES loans(l_id),
    FOREIGN KEY(uemi_id) REFERENCES users(u_id)
	);
ALTER TABLE emi_schedule AUTO_INCREMENT=7028001;

SELECT * FROM emi_schedule;




SELECT * FROM users;

SELECT * FROM transactions;

SELECT * FROM loans;

SELECT * FROM emi_schedule;

USE bank_db;


