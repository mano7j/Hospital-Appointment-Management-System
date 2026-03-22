-- ═══════════════════════════════════════════════════════════════
--   HOSPITAL APPOINTMENT MANAGEMENT SYSTEM — MySQL Schema
-- ═══════════════════════════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- ─── PATIENT ────────────────────────────────────────────────────
CREATE TABLE Patient (
    Patient_ID   INT AUTO_INCREMENT PRIMARY KEY,
    Name         VARCHAR(100) NOT NULL,
    Age          INT          NOT NULL,
    Gender       ENUM('Male','Female','Other') NOT NULL,
    Phone        VARCHAR(15)  NOT NULL,
    Email        VARCHAR(100) NOT NULL UNIQUE,
    Address      TEXT,
    Password     VARCHAR(255) NOT NULL,
    Created_At   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ─── DOCTOR ─────────────────────────────────────────────────────
CREATE TABLE Doctor (
    Doctor_ID       INT AUTO_INCREMENT PRIMARY KEY,
    Doctor_Name     VARCHAR(100) NOT NULL,
    Specialization  VARCHAR(100) NOT NULL,
    Phone           VARCHAR(15)  NOT NULL,
    Email           VARCHAR(100) NOT NULL UNIQUE,
    Available_Days  VARCHAR(100),          -- e.g. "Mon,Wed,Fri"
    Available_Time  VARCHAR(50),           -- e.g. "09:00-17:00"
    Created_At      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── APPOINTMENT ────────────────────────────────────────────────
CREATE TABLE Appointment (
    Appointment_ID   INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID       INT NOT NULL,
    Doctor_ID        INT NOT NULL,
    Appointment_Date DATE NOT NULL,
    Appointment_Time TIME NOT NULL,
    Status           ENUM('Pending','Confirmed','Completed','Cancelled')
                     DEFAULT 'Pending',
    Reason           TEXT,
    Created_At       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
    FOREIGN KEY (Doctor_ID)  REFERENCES Doctor(Doctor_ID)   ON DELETE CASCADE
);

-- ─── ADMIN ──────────────────────────────────────────────────────
CREATE TABLE Admin (
    Admin_ID   INT AUTO_INCREMENT PRIMARY KEY,
    Username   VARCHAR(50)  NOT NULL UNIQUE,
    Password   VARCHAR(255) NOT NULL,         -- SHA-256 hashed
    Created_At TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ─── SEED DATA ──────────────────────────────────────────────────

-- Default admin (password: admin123 → SHA-256)
INSERT INTO Admin (Username, Password) VALUES
('admin', SHA2('admin123', 256));

-- Sample doctors
INSERT INTO Doctor (Doctor_Name, Specialization, Phone, Email, Available_Days, Available_Time) VALUES
('Dr. Priya Sharma',   'Cardiology',     '9876543210', 'priya@hospital.com',   'Mon,Wed,Fri', '09:00-17:00'),
('Dr. Arjun Mehta',    'Neurology',      '9876543211', 'arjun@hospital.com',   'Tue,Thu,Sat', '10:00-18:00'),
('Dr. Kavitha Raj',    'Orthopedics',    '9876543212', 'kavitha@hospital.com', 'Mon,Tue,Wed', '08:00-16:00'),
('Dr. Suresh Kumar',   'Dermatology',    '9876543213', 'suresh@hospital.com',  'Wed,Fri',     '11:00-19:00'),
('Dr. Meena Nair',     'Pediatrics',     '9876543214', 'meena@hospital.com',   'Mon,Thu,Fri', '09:00-15:00'),
('Dr. Ravi Chandran',  'General Medicine','9876543215', 'ravi@hospital.com',   'Mon,Tue,Wed,Thu,Fri', '09:00-17:00');

-- Sample patients (password: pass123 → SHA-256)
INSERT INTO Patient (Name, Age, Gender, Phone, Email, Address, Password) VALUES
('Anitha Krishnan',  32, 'Female', '9000000001', 'anitha@gmail.com', '12, MG Road, Coimbatore', SHA2('pass123', 256)),
('Rajesh Babu',      45, 'Male',   '9000000002', 'rajesh@gmail.com', '34, Anna Nagar, Chennai',  SHA2('pass123', 256)),
('Sujatha Devi',     28, 'Female', '9000000003', 'sujatha@gmail.com','7, Gandhi St, Madurai',    SHA2('pass123', 256));

-- Sample appointments
INSERT INTO Appointment (Patient_ID, Doctor_ID, Appointment_Date, Appointment_Time, Status, Reason) VALUES
(1, 1, CURDATE(), '10:00:00', 'Confirmed', 'Chest pain follow-up'),
(2, 3, CURDATE(), '14:00:00', 'Pending',   'Knee pain evaluation'),
(3, 5, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '09:30:00', 'Pending', 'Child vaccination'),
(1, 6, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '11:00:00', 'Pending', 'General checkup'),
(2, 2, DATE_SUB(CURDATE(), INTERVAL 3 DAY), '15:00:00', 'Completed','Headache assessment');

-- ─── USEFUL VIEWS ───────────────────────────────────────────────

-- Full appointment details
CREATE OR REPLACE VIEW vw_Appointments AS
SELECT
    a.Appointment_ID,
    a.Appointment_Date,
    a.Appointment_Time,
    a.Status,
    a.Reason,
    p.Patient_ID,
    p.Name        AS Patient_Name,
    p.Phone       AS Patient_Phone,
    d.Doctor_ID,
    d.Doctor_Name,
    d.Specialization
FROM Appointment a
JOIN Patient p ON a.Patient_ID = p.Patient_ID
JOIN Doctor  d ON a.Doctor_ID  = d.Doctor_ID;

-- Today's appointments
CREATE OR REPLACE VIEW vw_TodayAppointments AS
SELECT * FROM vw_Appointments
WHERE Appointment_Date = CURDATE()
ORDER BY Appointment_Time;
