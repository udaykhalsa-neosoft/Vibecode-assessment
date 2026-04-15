from utils.db import execute_query


class User:
    def __init__(self, username, email, password, id=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    def save(self):
        query = "INSERT INTO users (username, email, password) VALUES (?, ?, ?)"
        self.id = execute_query(
            query, (self.username, self.email, self.password), commit=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password
        }

    @staticmethod
    def get_by_id(user_id):
        query = "SELECT * FROM users WHERE id = ?"
        row = execute_query(query, (user_id,), fetchone=True)
        if row:
            return User(row['username'], row['email'], row['password'], id=row['id'])
        return None

    @staticmethod
    def get_by_username(username):
        query = "SELECT * FROM users WHERE username = ?"
        row = execute_query(query, (username,), fetchone=True)
        if row:
            return User(row['username'], row['email'], row['password'], id=row['id'])
        return None

    @staticmethod
    def get_all():
        query = "SELECT * FROM users"
        rows = execute_query(query, fetchall=True)
        return [User(row['username'], row['email'], row['password'], id=row['id']) for row in rows]

    @staticmethod
    def update_password(user_id, new_password):
        query = "UPDATE users SET password = ? WHERE id = ?"
        execute_query(query, (new_password, user_id), commit=True)

    def is_admin(self):
        return True


class Patient:
    def __init__(self, name, age, gender, phone, address, id=None, created_at=None):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender
        self.phone = phone
        self.address = address
        self.created_at = created_at

    def save(self):
        query = "INSERT INTO patients (name, age, gender, phone, address) VALUES (?, ?, ?, ?, ?)"
        self.id = execute_query(
            query, (self.name, self.age, self.gender, self.phone, self.address), commit=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at
        }

    @staticmethod
    def get_by_id(patient_id):
        query = "SELECT * FROM patients WHERE id = ?"
        row = execute_query(query, (patient_id,), fetchone=True)
        if row:
            return Patient(row['name'], row['age'], row['gender'], row['phone'], row['address'], id=row['id'], created_at=row['created_at'])
        return None

    def calculate_age_group(self):
        if self.age < 18:
            return 'child'
        elif self.age < 60:
            return 'adult'
        else:
            return 'senior'


class Doctor:
    def __init__(self, name, specialization, phone, email, available=True, id=None):
        self.id = id
        self.name = name
        self.specialization = specialization
        self.phone = phone
        self.email = email
        self.available = available

    def save(self):
        query = "INSERT INTO doctors (name, specialization, phone, email, available) VALUES (?, ?, ?, ?, ?)"
        self.id = execute_query(query, (self.name, self.specialization,
                                self.phone, self.email, self.available), commit=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'specialization': self.specialization,
            'phone': self.phone,
            'email': self.email,
            'available': bool(self.available)
        }

    @staticmethod
    def get_by_id(doctor_id):
        query = "SELECT * FROM doctors WHERE id = ?"
        row = execute_query(query, (doctor_id,), fetchone=True)
        if row:
            return Doctor(row['name'], row['specialization'], row['phone'], row['email'], available=row['available'], id=row['id'])
        return None

    @staticmethod
    def get_by_specialization(specialization):
        query = "SELECT * FROM doctors WHERE specialization = ?"
        rows = execute_query(query, (specialization,), fetchall=True)
        return [Doctor(row['name'], row['specialization'], row['phone'], row['email'], available=row['available'], id=row['id']) for row in rows]

    @staticmethod
    def get_available_slots(doctor_id, target_date):
        """
        Generates available 1-hour slots for a doctor on a specific date (9 AM - 5 PM).
        target_date format: 'YYYY-MM-DD'
        """

        standard_slots = [
            f"{target_date} {hour:02d}:00:00" for hour in range(9, 17)
        ]

        query = """
            SELECT appointment_date FROM appointments 
            WHERE doctor_id = ? AND appointment_date LIKE ? AND status != 'cancelled'
        """
        date_pattern = f"{target_date}%"
        rows = execute_query(query, (doctor_id, date_pattern), fetchall=True)

        booked_slots = [row['appointment_date'] for row in rows]

        available_slots = [
            slot for slot in standard_slots if slot not in booked_slots]

        return available_slots

    def is_available_status(self):
        query = "SELECT available FROM doctors WHERE id = ?"
        result = execute_query(query, (self.id,), fetchone=True)
        return bool(result['available']) if result else False


class Appointment:
    def __init__(self, patient_id, doctor_id, appointment_date, notes='', status='scheduled', id=None, created_at=None):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.status = status
        self.notes = notes
        self.created_at = created_at

    def save(self):
        query = "INSERT INTO appointments (patient_id, doctor_id, appointment_date, notes, status) VALUES (?, ?, ?, ?, ?)"
        self.id = execute_query(query, (self.patient_id, self.doctor_id,
                                self.appointment_date, self.notes, self.status), commit=True)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at
        }

    @staticmethod
    def get_by_id(appointment_id):
        query = "SELECT * FROM appointments WHERE id = ?"
        row = execute_query(query, (appointment_id,), fetchone=True)
        if row:
            return Appointment(row['patient_id'], row['doctor_id'], row['appointment_date'], notes=row['notes'], status=row['status'], id=row['id'], created_at=row['created_at'])
        return None

    @staticmethod
    def update_status(appointment_id, status):
        query = "UPDATE appointments SET status = ? WHERE id = ?"
        execute_query(query, (status, appointment_id), commit=True)


class MedicalRecord:
    def __init__(self, patient_id, doctor_id, diagnosis, prescription, id=None, visit_date=None):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.diagnosis = diagnosis
        self.prescription = prescription
        self.visit_date = visit_date

    def save(self):
        query = "INSERT INTO medical_records (patient_id, doctor_id, diagnosis, prescription) VALUES (?, ?, ?, ?)"
        self.id = execute_query(
            query, (self.patient_id, self.doctor_id, self.diagnosis, self.prescription), commit=True)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'visit_date': self.visit_date
        }

    @staticmethod
    def get_by_patient(patient_id):
        query = "SELECT * FROM medical_records WHERE patient_id = ?"
        rows = execute_query(query, (patient_id,), fetchall=True)
        return [MedicalRecord(row['patient_id'], row['doctor_id'], row['diagnosis'], row['prescription'], id=row['id'], visit_date=row['visit_date']) for row in rows]


def get_patient_statistics():
    query = "SELECT COUNT(*) as total, AVG(age) as avg_age FROM patients"
    row = execute_query(query, fetchone=True)
    return {'total_patients': row['total'], 'average_age': row['avg_age'] if row['avg_age'] else 0}


def get_appointment_summary():
    query = "SELECT status, COUNT(*) as count FROM appointments GROUP BY status"
    rows = execute_query(query, fetchall=True)
    return {row['status']: row['count'] for row in rows}


def get_hospital_stats_combined():
    """Consolidated logic for the hospital /stats endpoints."""
    stats = {}
    stats['patient_count'] = execute_query(
        "SELECT COUNT(*) as count FROM patients", fetchone=True)['count']
    stats['doctor_count'] = execute_query(
        "SELECT COUNT(*) as count FROM doctors", fetchone=True)['count']
    stats['total_appointments'] = execute_query(
        "SELECT COUNT(*) as count FROM appointments", fetchone=True)['count']

    scheduled = execute_query(
        "SELECT COUNT(*) as count FROM appointments WHERE status = 'scheduled'", fetchone=True)['count']
    completed = execute_query(
        "SELECT COUNT(*) as count FROM appointments WHERE status = 'completed'", fetchone=True)['count']

    stats['scheduled_appointments'] = scheduled
    stats['completed_appointments'] = completed

    total_tracked = scheduled + completed
    stats['completion_rate'] = (
        completed / total_tracked * 100) if total_tracked > 0 else 0

    return stats
