import json
from tests.base_test import BaseTestCase
from utils.db import execute_query
from app import app


class TestHospital(BaseTestCase):

    def setUp(self):
        super().setUp()

        with app.app_context():
            query = "INSERT INTO doctors (name, specialization, phone, email) VALUES (?, ?, ?, ?)"
            execute_query(query, ('Dr. Smith', 'Cardiology',
                          '555-0000', 'smith@hospital.com'), commit=True)

    def test_create_and_get_patient(self):
        """Test creating a patient and retrieving their details."""
        post_res = self.client.post('/hospital/patients', json={
            'name': 'Jane Doe',
            'age': 35,
            'gender': 'Female',
            'phone': '555-1234',
            'address': '123 Main St'
        })
        self.assertEqual(post_res.status_code, 201)
        patient_id = json.loads(post_res.data)['id']

        get_res = self.client.get(f'/hospital/patients/{patient_id}')
        data = json.loads(get_res.data)
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(data['name'], 'Jane Doe')

    def test_update_patient(self):
        """Test updating existing patient information."""
        post_res = self.client.post('/hospital/patients', json={
            'name': 'Mark', 'age': 40, 'gender': 'Male', 'phone': '000', 'address': 'Nowhere'
        })
        patient_id = json.loads(post_res.data)['id']

        put_res = self.client.put(f'/hospital/patients/{patient_id}', json={
            'phone': '999-9999'
        })
        self.assertEqual(put_res.status_code, 200)

        get_res = self.client.get(f'/hospital/patients/{patient_id}')
        self.assertEqual(json.loads(get_res.data)['phone'], '999-9999')

    def test_get_doctors(self):
        """Test retrieving the list of doctors and filtering by specialization."""
        res = self.client.get('/hospital/doctors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]['name'], 'Dr. Smith')

        res_filtered = self.client.get(
            '/hospital/doctors?specialization=Cardiology')
        self.assertEqual(len(json.loads(res_filtered.data)), 1)

    def test_doctor_availability(self):
        """Test checking a doctor's available time slots."""
        date_str = '2026-04-20'

        res = self.client.get(
            f'/hospital/doctors/1/availability?date={date_str}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['total_available'], 8)

        self.client.post('/hospital/patients', json={
                         'name': 'Alice', 'age': 30, 'gender': 'F', 'phone': '123', 'address': 'B'})
        self.client.post('/hospital/appointments', json={
            'patient_id': 1,
            'doctor_id': 1,
            'appointment_date': f'{date_str} 10:00:00',
            'notes': 'Checkup'
        })

        res_after = self.client.get(
            f'/hospital/doctors/1/availability?date={date_str}')
        data_after = json.loads(res_after.data)
        self.assertEqual(res_after.status_code, 200)
        self.assertEqual(data_after['total_available'], 7)
        self.assertNotIn(f'{date_str} 10:00:00', data_after['available_slots'])

    def test_appointments_flow(self):
        """Test booking and updating an appointment."""
        self.client.post('/hospital/patients', json={
                         'name': 'Bob', 'age': 50, 'gender': 'M', 'phone': '1', 'address': 'A'})

        post_res = self.client.post('/hospital/appointments', json={
            'patient_id': 1,
            'doctor_id': 1,
            'appointment_date': '2026-05-01 10:00:00',
            'notes': 'Heart checkup'
        })
        self.assertEqual(post_res.status_code, 201)
        appointment_id = json.loads(post_res.data)['id']

        put_res = self.client.put(f'/hospital/appointments/{appointment_id}/status', json={
            'status': 'completed'
        })
        self.assertEqual(put_res.status_code, 200)

    def test_medical_records(self):
        """Test creating and fetching medical records."""
        post_res = self.client.post('/hospital/medical-records', json={
            'patient_id': 1,
            'doctor_id': 1,
            'diagnosis': 'Healthy',
            'prescription': 'Vitamins'
        })
        self.assertEqual(post_res.status_code, 201)

        get_res = self.client.get('/hospital/medical-records?patient_id=1')
        data = json.loads(get_res.data)
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(data[0]['diagnosis'], 'Healthy')
