from datetime import datetime

from flask import Blueprint, request, jsonify
from models import Patient, Doctor, Appointment, MedicalRecord, get_hospital_stats_combined
from utils.db import execute_query

hospital_bp = Blueprint('hospital', __name__)


@hospital_bp.route('/patients', methods=['GET'])
def get_patients():
    search = request.args.get('search', '')
    limit = request.args.get('limit', 100)

    if search:
        query = "SELECT * FROM patients WHERE name LIKE ? OR phone LIKE ? LIMIT ?"
        search_term = f"%{search}%"
        rows = execute_query(
            query, (search_term, search_term, limit), fetchall=True)
    else:
        query = "SELECT * FROM patients LIMIT ?"
        rows = execute_query(query, (limit,), fetchall=True)

    patients = [Patient(**row).to_dict() for row in rows]
    return jsonify(patients)


@hospital_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = Patient.get_by_id(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    return jsonify(patient.to_dict())


@hospital_bp.route('/patients', methods=['POST'])
def create_patient():
    data = request.json
    new_patient = Patient(
        name=data.get('name'),
        age=data.get('age'),
        gender=data.get('gender'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    new_patient.save()
    return jsonify({'message': 'Patient created successfully', 'id': new_patient.id}), 201


@hospital_bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    data = request.json
    updates = []
    params = []

    for field in ['name', 'age', 'gender', 'phone', 'address']:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    params.append(patient_id)
    set_clause = ', '.join(updates)
    query = f"UPDATE patients SET {set_clause} WHERE id = ?"

    execute_query(query, tuple(params), commit=True)
    return jsonify({'message': 'Patient updated successfully'})


@hospital_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    execute_query("DELETE FROM patients WHERE id = ?",
                  (patient_id,), commit=True)
    return jsonify({'message': 'Patient deleted successfully'})


@hospital_bp.route('/search/patients', methods=['GET'])
def search_patients():
    """Maintained to ensure compatibility with any frontend calling the explicit /search route"""
    keyword = request.args.get('q', '')
    query = "SELECT * FROM patients WHERE name LIKE ? OR phone LIKE ? OR address LIKE ?"
    search_term = f"%{keyword}%"

    rows = execute_query(
        query, (search_term, search_term, search_term), fetchall=True)
    patients = [Patient(**row).to_dict() for row in rows]
    return jsonify(patients)


@hospital_bp.route('/doctors', methods=['GET'])
def get_doctors():
    specialization = request.args.get('specialization', '')
    limit = request.args.get('limit', 50)

    if specialization:
        query = "SELECT * FROM doctors WHERE specialization = ? LIMIT ?"
        rows = execute_query(query, (specialization, limit), fetchall=True)
    else:
        query = "SELECT * FROM doctors LIMIT ?"
        rows = execute_query(query, (limit,), fetchall=True)

    doctors = [Doctor(**row).to_dict() for row in rows]
    return jsonify(doctors)


@hospital_bp.route('/appointments', methods=['GET'])
def get_appointments():
    patient_id = request.args.get('patient_id')
    doctor_id = request.args.get('doctor_id')

    where_clauses = []
    params = []

    if patient_id:
        where_clauses.append("patient_id = ?")
        params.append(patient_id)
    if doctor_id:
        where_clauses.append("doctor_id = ?")
        params.append(doctor_id)

    query = "SELECT * FROM appointments"
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    rows = execute_query(query, tuple(params), fetchall=True)
    appointments = [Appointment(**row).to_dict() for row in rows]
    return jsonify(appointments)


@hospital_bp.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.json
    new_appointment = Appointment(
        patient_id=data.get('patient_id'),
        doctor_id=data.get('doctor_id'),
        appointment_date=data.get('appointment_date'),
        notes=data.get('notes', '')
    )
    new_appointment.save()
    return jsonify({'message': 'Appointment created successfully', 'id': new_appointment.id}), 201


@hospital_bp.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
def update_appointment_status(appointment_id):
    data = request.json
    status = data.get('status')
    if not status:
        return jsonify({'error': 'Status is required'}), 400

    Appointment.update_status(appointment_id, status)
    return jsonify({'message': 'Appointment status updated successfully'})


@hospital_bp.route('/medical-records', methods=['GET'])
def get_medical_records():
    patient_id = request.args.get('patient_id')

    if patient_id:
        records = MedicalRecord.get_by_patient(patient_id)
    else:
        query = "SELECT * FROM medical_records"
        rows = execute_query(query, fetchall=True)
        records = [MedicalRecord(**row) for row in rows]

    return jsonify([record.to_dict() for record in records])


@hospital_bp.route('/medical-records', methods=['POST'])
def create_medical_record():
    data = request.json
    new_record = MedicalRecord(
        patient_id=data.get('patient_id'),
        doctor_id=data.get('doctor_id'),
        diagnosis=data.get('diagnosis'),
        prescription=data.get('prescription')
    )
    new_record.save()
    return jsonify({'message': 'Medical record created successfully', 'id': new_record.id}), 201


@hospital_bp.route('/stats', methods=['GET'])
def get_hospital_stats():
    stats = get_hospital_stats_combined()
    return jsonify(stats)


@hospital_bp.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
def check_doctor_availability(doctor_id):
    """
    Check a doctor's available time slots for a specific date.
    Query Param: ?date=YYYY-MM-DD (Defaults to today if omitted)
    """
    date_str = request.args.get('date')

    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD'}), 400

    doctor = Doctor.get_by_id(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404

    available_slots = Doctor.get_available_slots(doctor_id, date_str)

    return jsonify({
        'doctor_id': doctor_id,
        'doctor_name': doctor.name,
        'date': date_str,
        'total_available': len(available_slots),
        'available_slots': available_slots
    }), 200
