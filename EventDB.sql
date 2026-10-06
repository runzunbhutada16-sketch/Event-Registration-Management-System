-- =========================================================
-- DBMS MINI PROJECT
-- EVENT REGISTRATION MANAGEMENT SYSTEM
-- MySQL 8.0
-- =========================================================


-- =========================================================
-- 1. CREATE DATABASE
-- =========================================================

DROP DATABASE IF EXISTS EventDB;

CREATE DATABASE EventDB;

USE EventDB;


-- =========================================================
-- 2. CREATE USERS TABLE
-- =========================================================

CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 3. CREATE EVENTS TABLE
-- =========================================================

CREATE TABLE Events (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    venue VARCHAR(150) NOT NULL,
    capacity INT NOT NULL,
    description VARCHAR(255),

    CHECK (capacity > 0)
);


-- =========================================================
-- 4. CREATE REGISTRATIONS TABLE
-- =========================================================

CREATE TABLE Registrations (
    registration_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_registration_user
        FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_registration_event
        FOREIGN KEY (event_id)
        REFERENCES Events(event_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    -- Same user cannot register for same event twice
    CONSTRAINT unique_user_event
        UNIQUE (user_id, event_id)
);


-- =========================================================
-- 5. INSERT USERS
-- =========================================================

INSERT INTO Users (name, email, phone)
VALUES
('Runzun Bhutada', 'runzun@example.com', '9876543210'),
('Vedika Sharma', 'vedika@example.com', '9876543211'),
('Divya Baghele', 'divya@example.com', '9876543212'),
('Anshika Patil', 'anshika@example.com', '9876543213'),
('Rahul Verma', 'rahul@example.com', '9876543214'),
('Priya Joshi', 'priya@example.com', '9876543215');


-- =========================================================
-- 6. INSERT EVENTS
-- =========================================================

INSERT INTO Events
(title, event_date, venue, capacity, description)
VALUES
('Tech Symposium', '2026-10-15',
 'IT Seminar Hall', 100,
 'Technical symposium for students'),

('AI Workshop', '2026-10-20',
 'Computer Lab', 50,
 'Introduction to Artificial Intelligence'),

('Web Dev Bootcamp', '2026-10-25',
 'E-303 Lab', 60,
 'Hands-on web development workshop'),

('Data Analytics Seminar', '2026-11-05',
 'Auditorium', 150,
 'Seminar on Data Analytics and Business Intelligence'),

('Cyber Security Workshop', '2026-11-12',
 'IT Seminar Hall', 80,
 'Basic concepts of cyber security');


-- =========================================================
-- 7. INSERT REGISTRATIONS
-- =========================================================

INSERT INTO Registrations (user_id, event_id)
VALUES
(1, 1),
(2, 1),
(3, 2),
(4, 3),
(2, 3),
(5, 4),
(6, 4),
(1, 5);


-- =========================================================
-- 8. DISPLAY ALL USERS
-- READ OPERATION
-- =========================================================

SELECT * FROM Users;


-- =========================================================
-- 9. DISPLAY ALL EVENTS
-- =========================================================

SELECT * FROM Events;


-- =========================================================
-- 10. DISPLAY ALL REGISTRATIONS
-- =========================================================

SELECT * FROM Registrations;


-- =========================================================
-- 11. JOIN QUERY
-- Display registered users with event details
-- =========================================================

SELECT
    r.registration_id,
    u.name AS attendee_name,
    u.email,
    e.title AS event_title,
    e.event_date,
    e.venue,
    r.registration_date
FROM Registrations r
JOIN Users u
    ON r.user_id = u.user_id
JOIN Events e
    ON r.event_id = e.event_id;


-- =========================================================
-- 12. COUNT REGISTRATIONS FOR EACH EVENT
-- GROUP BY + LEFT JOIN
-- =========================================================

SELECT
    e.event_id,
    e.title AS event_title,
    COUNT(r.registration_id) AS total_registered
FROM Events e
LEFT JOIN Registrations r
    ON e.event_id = r.event_id
GROUP BY e.event_id, e.title;


-- =========================================================
-- 13. EVENTS WITH NO REGISTRATIONS
-- =========================================================

SELECT
    e.event_id,
    e.title,
    e.event_date,
    e.venue
FROM Events e
LEFT JOIN Registrations r
    ON e.event_id = r.event_id
WHERE r.registration_id IS NULL;


-- =========================================================
-- 14. USERS REGISTERED FOR A PARTICULAR EVENT
-- =========================================================

SELECT
    u.name,
    u.email,
    e.title
FROM Users u
JOIN Registrations r
    ON u.user_id = r.user_id
JOIN Events e
    ON r.event_id = e.event_id
WHERE e.event_id = 1;


-- =========================================================
-- 15. VIEW
-- EventAttendees
-- =========================================================

CREATE VIEW EventAttendees AS
SELECT
    r.registration_id,
    u.name AS attendee_name,
    u.email,
    e.title AS event_title,
    e.event_date,
    e.venue
FROM Registrations r
JOIN Users u
    ON r.user_id = u.user_id
JOIN Events e
    ON r.event_id = e.event_id;


-- =========================================================
-- 16. QUERY THE VIEW
-- =========================================================

SELECT * FROM EventAttendees;


-- =========================================================
-- 17. STORED PROCEDURE
-- Get registrations for a particular event
-- =========================================================

DELIMITER //

CREATE PROCEDURE GetEventRegistrations(IN eid INT)
BEGIN

    SELECT
        r.registration_id,
        u.name AS attendee_name,
        u.email,
        e.title AS event_title,
        e.event_date,
        e.venue
    FROM Registrations r
    JOIN Users u
        ON r.user_id = u.user_id
    JOIN Events e
        ON r.event_id = e.event_id
    WHERE e.event_id = eid;

END //

DELIMITER ;


-- =========================================================
-- 18. CALL STORED PROCEDURE
-- =========================================================

CALL GetEventRegistrations(1);


-- =========================================================
-- 19. CREATE AUDIT TABLE
-- Used for demonstrating TRIGGER
-- =========================================================

CREATE TABLE Registration_Audit (
    audit_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_id INT,
    user_id INT,
    event_id INT,
    action_type VARCHAR(30),
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 20. CREATE TRIGGER
-- Automatically records every new registration
-- =========================================================

DELIMITER //

CREATE TRIGGER after_registration_insert
AFTER INSERT ON Registrations
FOR EACH ROW
BEGIN

    INSERT INTO Registration_Audit
    (
        registration_id,
        user_id,
        event_id,
        action_type
    )
    VALUES
    (
        NEW.registration_id,
        NEW.user_id,
        NEW.event_id,
        'NEW REGISTRATION'
    );

END //

DELIMITER ;


-- =========================================================
-- 21. TEST THE TRIGGER
-- =========================================================

INSERT INTO Registrations (user_id, event_id)
VALUES (3, 5);


-- =========================================================
-- 22. VIEW AUDIT RECORDS
-- =========================================================

SELECT * FROM Registration_Audit;


-- =========================================================
-- 23. UPDATE OPERATION
-- CRUD - UPDATE
-- =========================================================

UPDATE Users
SET phone = '9999999999'
WHERE user_id = 1;

SELECT * FROM Users
WHERE user_id = 1;


-- =========================================================
-- 24. CREATE OPERATION
-- CRUD - CREATE
-- =========================================================

INSERT INTO Users
(name, email, phone)
VALUES
('Test Student', 'test@example.com', '9000000000');

SELECT * FROM Users;


-- =========================================================
-- 25. DELETE OPERATION
-- CRUD - DELETE
-- =========================================================

DELETE FROM Users
WHERE email = 'test@example.com';


-- Verify deletion
SELECT * FROM Users;


-- =========================================================
-- 26. TRANSACTION - COMMIT
-- =========================================================

START TRANSACTION;

INSERT INTO Registrations
(user_id, event_id)
VALUES
(4, 5);

COMMIT;


-- Verify committed transaction
SELECT * FROM Registrations;


-- =========================================================
-- 27. TRANSACTION - ROLLBACK DEMONSTRATION
-- =========================================================

START TRANSACTION;

INSERT INTO Registrations
(user_id, event_id)
VALUES
(5, 2);

ROLLBACK;


-- Verify rollback
SELECT * FROM Registrations;


-- =========================================================
-- 28. FINAL DATABASE CHECK
-- =========================================================

SHOW TABLES;


-- =========================================================
-- 29. FINAL VIEW
-- =========================================================

SELECT * FROM EventAttendees;


-- =========================================================
-- END OF PROJECT
-- =========================================================