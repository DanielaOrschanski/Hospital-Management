from flask import Flask, jsonify, request
from flask_restx import Api, reqparse, Resource
from hospital_json_utils import HospitalJsonEncoder
#from JustClasses import Hospital, Doctor, Patient, Pharmacy, Appointment, Request, MedicineRequest, AppointmentRequest, Order
from HospitalClasses import *
import datetime

my_hospital = Hospital()

hospital_app = Flask(__name__)
# need to extend this class for custom objects, so that they can be jsonified
hospital_app.json_encoder = HospitalJsonEncoder
hospital_api: Api = Api(hospital_app)

patient_parser = reqparse.RequestParser()
patient_parser.add_argument('name', type=str, required=True, location="form")
patient_parser.add_argument('age', type=int, required=True, help='The age of the patient, e.g., 22', location="form")
patient_parser.add_argument('email', type=str, required=True,
                            help='The email to contact the patient, e.g., daniela@gmail.com', location="form")

doctor_parser = reqparse.RequestParser()
doctor_parser.add_argument('name', type=str, required=True, help='The surname of the doctor, e.g., Orschanski',
                           location="form")
doctor_parser.add_argument('department', type=str, required=True,
                           help='The speciality of the doctor, e.g., pediatrician', location="form")
doctor_parser.add_argument('email', type=str, required=True,
                           help='The email to contact the patient, e.g., daniela@gmail.com', location="form")

pharmacy_parser = reqparse.RequestParser()
pharmacy_parser.add_argument('name', type=str, required=True, help='The name of the pharmacy, e.g., Vienna´s Pharmacy',
                             location="form")

# book Appointment param:
info_app_parser = reqparse.RequestParser()
info_app_parser.add_argument('info', type=str, required=True,
                             help='Indicate the date, time, duration and cost of the appointment (separated by comas), e.g., 21-05-2022 , 11:00 , 30 , 100 ',
                             location="form")

# Order medicine param:
info_ord_parser = reqparse.RequestParser()
info_ord_parser.add_argument('info', type=str, required=True,
                             help='Indicate the cost and the medicine asked in the order(separated by comas), e.g., 100, ibuprofene ',
                             location="form")

# request_app_id_parser= reqparse.RequestParser()
# request_app_id_parser.add_argument('request_app_id', type=str, required=True, help='The ID of the request of appointment, e.g., cb639e64-282e-4056-b7e3-bfb7094f8eb9 ', location = "form")

order_parser = reqparse.RequestParser()
order_parser.add_argument('cost', type=int, required=True, help='The cost of the order, e.g., 30', location="form")
order_parser.add_argument('medicine', type=str, required=True, help='The medicine ordered, e.g., 30', location="form")

request_parser = reqparse.RequestParser()
request_parser.add_argument('from', type=str, required=True, help='The cost of the order, e.g., 30', location="form")
request_parser.add_argument('to', type=str, required=True, help='The medicine ordered, e.g., 30', location="form")



@hospital_api.route('/patient')
class AddPatientAPI(Resource):
    @hospital_api.doc(parser=patient_parser)
    def post(self):
        # get the post parameters
        args = patient_parser.parse_args()
        name = args['name']
        age = args['age']
        email = args['email']
        # create a new patient object
        # new_patient = Patient(name, age, email)
        new_patient = Patient(name, age, email)
        my_hospital.addPatient(new_patient)
        session.add(new_patient)
        session.commit()
        # add the animal to the zoo
        patient_dict = {
            "id": new_patient.id,
            "name": new_patient.name
        }
        return jsonify(patient_dict)


@hospital_api.route('/patient/<patient_id>')
class Patient_ID(Resource):
    def get(self, patient_id):
        search_result = my_hospital.getPatient(patient_id)
        return jsonify(search_result)  # this is automatically jsonified by flask-restx

    def delete(self, patient_id):
        targeted_patient = my_hospital.getPatient(patient_id)
        if not targeted_patient:
            return jsonify(f"Patient with ID {patient_id} was not found")
        my_hospital.removePatient(targeted_patient)
        return jsonify(f"Patient with ID {patient_id} was removed")


@hospital_api.route('/patients')
class AllPatients(Resource):
    def get(self):
        patients = list(session.query(Patient))
        return jsonify(patients)

        #patients_dict = {}
        #for p in my_hospital.patients:
         #   patients_dict.update({"id":p.id,
         #                         "name": p.name,
         #                         })

        #return jsonify(patients_dict)
        #return jsonify(my_hospital.patients)


# ----------------------------------------------------------------------------------------------------------
@hospital_api.route('/doctor')
class AddDoctorAPI(Resource):
    @hospital_api.doc(parser=doctor_parser)
    def post(self):
        # get the post parameters
        args = doctor_parser.parse_args()
        name = args['name']
        email = args['email']
        department = args['department']
        # create a new patient object
        # new_doctor = Doctor(name, department, email)
        new_doctor = Doctor(name, department, email)
        my_hospital.addDoctor(new_doctor)
        session.add(new_doctor)
        session.commit()
        # add the doctor to the hospital

        doctor_dict = {
            "id": new_doctor.id,
            "name": new_doctor.name
        }
        return jsonify(doctor_dict)


@hospital_api.route('/doctor/<doctor_id>')
class Doctor_ID(Resource):
    def get(self, doctor_id):
        search_result = my_hospital.getDoctor(doctor_id)
        return jsonify(search_result)

    def delete(self, doctor_id):
        targeted_doctor = my_hospital.getDoctor(doctor_id)
        if not targeted_doctor:
            return jsonify(f"Doctor with ID {doctor_id} was not found")
        my_hospital.removeDoctor(targeted_doctor)
        return jsonify(f"Doctor with ID {doctor_id} was removed")


@hospital_api.route('/doctors')
class AllDoctors(Resource):
    def get(self):
        doctors_dict = {}
        for d in my_hospital.doctors:
            doctors_dict.update({"id": d.id,
                                  "name": d.name,
                                  })

        return jsonify(doctors_dict)
        #return jsonify(my_hospital.doctors)


# ----------------------------------------------------------------------------------------------------------
@hospital_api.route('/pharmacy')
class AddPharmacyAPI(Resource):
    @hospital_api.doc(parser=pharmacy_parser)
    def post(self):
        args = pharmacy_parser.parse_args()
        name = args['name']
        new_pharmacy = Pharmacy(name)
        my_hospital.addPharmacy(new_pharmacy)
        session.add(new_pharmacy)
        session.commit()
        # add the doctor to the hospital

        pharmacy_dict = {
            "id": new_pharmacy.id,
            "name": new_pharmacy.name
        }
        return jsonify(pharmacy_dict)


@hospital_api.route('/pharmacy/<pharmacy_id>')
class Pharmacy_ID(Resource):
    def get(self, pharmacy_id):
        search_result = my_hospital.getPharmacy(pharmacy_id)
        return jsonify(search_result)

    def delete(self, pharmacy_id):
        targeted_pharmacy = my_hospital.getPharmacy(pharmacy_id)
        if not targeted_pharmacy:
            return jsonify(f"Pharmacy with ID {pharmacy_id} was not found")
        my_hospital.removePharmacy(targeted_pharmacy)
        return jsonify(f"Pharmacy with ID {pharmacy_id} was removed")


@hospital_api.route('/pharmacies')
class AllPharmacies(Resource):
    def get(self):
        return jsonify(my_hospital.pharmacies)


# -----------------------------------------------------------------------------------------------------------------

@hospital_api.route('/patients/<patient_id>/bookApointment/<doctor_id>')
class BookAppointment(Resource):
    @hospital_api.doc(parser=info_app_parser)
    def post(self, patient_id, doctor_id):
        targeted_patient = my_hospital.getPatient(patient_id)
        #targeted_patient = list(session.query(Patient).filter(Patient.id == patient_id))
        if not targeted_patient:
            return jsonify(f"Patient with ID {patient_id} was not found")

        targeted_doctor = my_hospital.getDoctor(doctor_id)
        #targeted_doctor = list(session.query(Doctor).filter(Doctor.id == doctor_id))
        if not targeted_doctor:
            return jsonify(f"Doctor with ID {doctor_id} was not found")

        #targeted_patient = targeted_patient[0]
        #targeted_doctor = targeted_doctor[0]
        args = info_app_parser.parse_args()
        info_app = args['info']

        info = info_app.split(",")
        date_app = info[0]
        time_app = info[1]
        duration_app = info[2]
        cost_app = info[3]
        #approved_app = info[4]
        request = targeted_patient.bookAppointment(targeted_doctor, date_app, time_app, duration_app, cost_app)
        session.add(request)
        session.commit()

        return jsonify({
            "message": f"{targeted_patient} has requested an appointment on {date_app} with the doctor {targeted_doctor}",
            "request's id": request.id
        })


@hospital_api.route('/doctors/<doctor_id>/orderMedicine/<pharmacy_id>')
class OrderMedicine(Resource):
    @hospital_api.doc(parser=info_ord_parser)
    def post(self, pharmacy_id, doctor_id):
        targeted_pharmacy = my_hospital.getPharmacy(pharmacy_id)
        if not targeted_pharmacy:
            return jsonify(f"Pharmacy with ID {pharmacy_id} was not found")

        targeted_doctor = my_hospital.getDoctor(doctor_id)
        if not targeted_doctor:
            return jsonify(f"Doctor with ID {doctor_id} was not found")

        args = info_ord_parser.parse_args()
        info_ord = args['info']
        info = info_ord.split(",")
        cost = info[0]
        medicine = info[1]
        order = targeted_doctor.orderMedicine(targeted_pharmacy, cost, medicine)
        session.add(order)
        session.commit()

        return jsonify({
            "message": f"{targeted_doctor} has made an order to {targeted_pharmacy}",
            "order's id": order.id
        })

@hospital_api.route('/doctors/<doctor_id>/ApproveAppointment/<request_app_id>')
class ApproveAppointment(Resource):
    def post(self, doctor_id, request_app_id):
        targeted_doctor = my_hospital.getDoctor(doctor_id)
        if not targeted_doctor:
            return jsonify(f"Doctor with ID {doctor_id} was not found")

        targeted_request = my_hospital.getRequest(request_app_id, doctor_id)
        if not targeted_request:
            return jsonify(f"Request with ID {request_app_id} was not found")

        targeted_doctor.approve(targeted_request, my_hospital)

        return jsonify(f"The doctor {targeted_doctor} has approved the request {targeted_request}")

@hospital_api.route('/doctors/<doctor_id>/RejectAppointment/<request_app_id>')
class RejectAppointment(Resource):
    def post(self, doctor_id, request_app_id):
        targeted_doctor = my_hospital.getDoctor(doctor_id)
        if not targeted_doctor:
            return jsonify(f"Doctor with ID {doctor_id} was not found")

        targeted_request = my_hospital.getRequest(request_app_id, doctor_id)
        if not targeted_request:
            return jsonify(f"Request with ID {request_app_id} was not found")

        targeted_doctor.reject(targeted_request, my_hospital)

        return jsonify(f"The doctor {targeted_doctor} has rejected the request {targeted_request}")

@hospital_api.route('/pharmacies/<pharmacy_id>/ApproveOrder/<request_ord_id>')
class ApproveOrder(Resource):
    def post(self, pharmacy_id, request_ord_id):
        targeted_pharmacy = my_hospital.getPharmacy(pharmacy_id)
        if not targeted_pharmacy:
            return jsonify(f"Pharmacy with ID {pharmacy_id} was not found")

        targeted_request = my_hospital.getRequestOrd(request_ord_id, pharmacy_id)
        if not targeted_request:
            return jsonify(f"Request with ID {request_ord_id} was not found")

        targeted_pharmacy.approve(targeted_request, my_hospital)

        return jsonify(f"The pharmacy {targeted_pharmacy} has approved the request {targeted_request}")

@hospital_api.route('/pharmacies/<pharmacy_id>/deliverMedicine/<order_id>')
class OrderMedicine(Resource):
    def post(self, pharmacy_id, order_id):
        targeted_pharmacy = my_hospital.getPharmacy(pharmacy_id)
        if not targeted_pharmacy:
            return jsonify(f"Pharmacy with ID {pharmacy_id} was not found")

        targeted_order = my_hospital.getRequestOrd(order_id, pharmacy_id)
        if not targeted_order:
            return jsonify(f"Order with ID {order_id} was not found")

        targeted_pharmacy.deliverMedicine(targeted_order)
        return jsonify(f"{targeted_pharmacy} has delivered the order {targeted_order}")

@hospital_api.route('/pharmacies/<pharmacy_id>/RejectOrder/<request_ord_id>')
class RejectOrder(Resource):
    def post(self, pharmacy_id, request_ord_id):
        targeted_pharmacy = my_hospital.getPharmacy(pharmacy_id)
        if not targeted_pharmacy:
            return jsonify(f"Pharmacy with ID {pharmacy_id} was not found")

        targeted_request = my_hospital.getRequestOrd(request_ord_id, pharmacy_id)
        if not targeted_request:
            return jsonify(f"Request with ID {request_ord_id} was not found")

        targeted_pharmacy.reject(targeted_request, my_hospital)

        return jsonify(f"The pharmacy {targeted_pharmacy} has rejected the request {targeted_request}")


@hospital_api.route('/doctors/<doctor_id>/cancelAppointment/<request_app_id>')
class CancelAppointment(Resource):
    def post(self, doctor_id, request_app_id):
        targeted_request = my_hospital.getRequest(request_app_id, doctor_id)
        if not targeted_request:
            return jsonify(f"Request with ID {request_app_id} was not found")

        my_hospital.cancelAppointment(targeted_request)
        return jsonify(f"The appointment which ID is {targeted_request} has been canceled")


if __name__ == '__main__':
    hospital_app.run(debug=True, port=7890)
