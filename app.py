from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import hashlib
import os
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# ─── DB CONFIG ────────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'database': 'hospital_db',
    'user': 'root',
    'password': 'your_password'
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def serve_index():
    return send_file('index.html')

# ─── AUTH ─────────────────────────────────────────────────────────────────────
@app.route('/api/patient/register', methods=['POST'])
def patient_register():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Patient (Name, Age, Gender, Phone, Email, Address, Password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data['name'], data['age'], data['gender'], data['phone'],
              data['email'], data['address'], hash_password(data['password'])))
        conn.commit()
        return jsonify({'success': True, 'message': 'Patient registered successfully'})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    finally:
        cursor.close(); conn.close()

@app.route('/api/patient/login', methods=['POST'])
def patient_login():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Patient WHERE Email=%s AND Password=%s",
                       (data['email'], hash_password(data['password'])))
        patient = cursor.fetchone()
        if patient:
            session['patient_id'] = patient['Patient_ID']
            session['role'] = 'patient'
            return jsonify({'success': True, 'patient': {k: v for k, v in patient.items() if k != 'Password'}})
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    finally:
        cursor.close(); conn.close()

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Admin WHERE Username=%s AND Password=%s",
                       (data['username'], hash_password(data['password'])))
        admin = cursor.fetchone()
        if admin:
            session['admin_id'] = admin['Admin_ID']
            session['role'] = 'admin'
            return jsonify({'success': True, 'admin': {k: v for k, v in admin.items() if k != 'Password'}})
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    finally:
        cursor.close(); conn.close()

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

# ─── PATIENTS ─────────────────────────────────────────────────────────────────
@app.route('/api/patients', methods=['GET'])
def get_patients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT Patient_ID, Name, Age, Gender, Phone, Email, Address FROM Patient")
        return jsonify(cursor.fetchall())
    finally:
        cursor.close(); conn.close()

@app.route('/api/patients/<int:pid>', methods=['GET'])
def get_patient(pid):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT Patient_ID, Name, Age, Gender, Phone, Email, Address FROM Patient WHERE Patient_ID=%s", (pid,))
        patient = cursor.fetchone()
        return jsonify(patient) if patient else (jsonify({'message': 'Not found'}), 404)
    finally:
        cursor.close(); conn.close()

@app.route('/api/patients/<int:pid>', methods=['PUT'])
def update_patient(pid):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Patient SET Name=%s, Age=%s, Gender=%s, Phone=%s, Email=%s, Address=%s
            WHERE Patient_ID=%s
        """, (data['name'], data['age'], data['gender'], data['phone'],
              data['email'], data['address'], pid))
        conn.commit()
        return jsonify({'success': True})
    finally:
        cursor.close(); conn.close()

@app.route('/api/patients/<int:pid>', methods=['DELETE'])
def delete_patient(pid):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Patient WHERE Patient_ID=%s", (pid,))
        conn.commit()
        return jsonify({'success': True})
    finally:
        cursor.close(); conn.close()

# ─── DOCTORS ──────────────────────────────────────────────────────────────────
@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Doctor")
        return jsonify(cursor.fetchall())
    finally:
        cursor.close(); conn.close()

@app.route('/api/doctors', methods=['POST'])
def add_doctor():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Doctor (Doctor_Name, Specialization, Phone, Email, Available_Days, Available_Time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['doctor_name'], data['specialization'], data['phone'],
              data['email'], data['available_days'], data['available_time']))
        conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    finally:
        cursor.close(); conn.close()

@app.route('/api/doctors/<int:did>', methods=['PUT'])
def update_doctor(did):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Doctor SET Doctor_Name=%s, Specialization=%s, Phone=%s,
            Email=%s, Available_Days=%s, Available_Time=%s WHERE Doctor_ID=%s
        """, (data['doctor_name'], data['specialization'], data['phone'],
              data['email'], data['available_days'], data['available_time'], did))
        conn.commit()
        return jsonify({'success': True})
    finally:
        cursor.close(); conn.close()

@app.route('/api/doctors/<int:did>', methods=['DELETE'])
def delete_doctor(did):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Doctor WHERE Doctor_ID=%s", (did,))
        conn.commit()
        return jsonify({'success': True})
    finally:
        cursor.close(); conn.close()

# ─── APPOINTMENTS ─────────────────────────────────────────────────────────────
@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT a.*, p.Name AS Patient_Name, d.Doctor_Name, d.Specialization
            FROM Appointment a
            JOIN Patient p ON a.Patient_ID = p.Patient_ID
            JOIN Doctor d ON a.Doctor_ID = d.Doctor_ID
            ORDER BY a.Appointment_Date DESC, a.Appointment_Time
        """)
        return jsonify(cursor.fetchall())
    finally:
        cursor.close(); conn.close()

@app.route('/api/appointments/patient/<int:pid>', methods=['GET'])
def get_patient_appointments(pid):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT a.*, d.Doctor_Name, d.Specialization
            FROM Appointment a
            JOIN Doctor d ON a.Doctor_ID = d.Doctor_ID
            WHERE a.Patient_ID=%s ORDER BY a.Appointment_Date DESC
        """, (pid,))
        return jsonify(cursor.fetchall())
    finally:
        cursor.close(); conn.close()

@app.route('/api/appointments', methods=['POST'])
def book_appointment():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Appointment (Patient_ID, Doctor_ID, Appointment_Date, Appointment_Time, Status, Reason)
            VALUES (%s, %s, %s, %s, 'Pending', %s)
        """, (data['patient_id'], data['doctor_id'], data['appointment_date'],
              data['appointment_time'], data.get('reason', '')))
        conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    finally:
        cursor.close(); conn.close()

@app.route('/api/appointments/<int:aid>', methods=['PUT'])
def update_appointment(aid):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Appointment SET Status=%s, Appointment_Date=%s,
            Appointment_Time=%s, Reason=%s WHERE Appointment_ID=%s
        """, (data['status'], data['appointment_date'],
              data['appointment_time'], data.get('reason', ''), aid))
        conn.commit()
        return jsonify({'success': True})
    finally:
        cursor.close(); conn.close()

@app.route('/api/appointments/<int:aid>', methods=['DELETE'])
def cancel_appointment(aid):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Appointment WHERE Appointment_ID=%s", (aid,))
        conn.commit()
        return jsonify({'success': True})
    finally:
        cursor.close(); conn.close()

# ─── DASHBOARD STATS ──────────────────────────────────────────────────────────
@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM Patient")
        patients = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS total FROM Doctor")
        doctors = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS total FROM Appointment")
        appointments = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS total FROM Appointment WHERE Status='Pending'")
        pending = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS total FROM Appointment WHERE Appointment_Date = CURDATE()")
        today = cursor.fetchone()['total']
        return jsonify({
            'patients': patients, 'doctors': doctors,
            'appointments': appointments, 'pending': pending, 'today': today
        })
    finally:
        cursor.close(); conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
