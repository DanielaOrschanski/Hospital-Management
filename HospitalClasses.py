import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, sessionmaker
import datetime
import uuid
import datetime
import copy

#1. Base Class
Base = declarative_base() #base class for all the domain classes
engine = create_engine('sqlite:///orms25.db', echo=True, connect_args={'check_same_thread': False}, pool_pre_ping=True) # te deja hacer operaciones desde distintos threads

#each table corresponds to a class
#each line of the table corresponds to an object
#each column of the table corresponds to an attribute of the object

#Base Class: format of the class to be SQL executable

#2. Domain Classes
##Domain Model or class: class that has a mapping into the database table
#They have to inherit from a specific base class
class Hospital(Base):
    __tablename__ = 'hospital'
    id = Column(String, primary_key=True)

    def __init__(self):
        self.doctors = []
        self.patients = []
        self.pharmacies = []

    def addDoctor(self, doctor):
        self.doctors.append(doctor)

    def getDoctor(self, doctor_id):
        for doctor in self.doctors:
            if doctor.id == doctor_id:
                return doctor

    def removeDoctor(self, doctor):
        self.doctors.remove(doctor)
        for patient in doctor.patients:
            patient.doctor = None

    def addPatient(self, patient):
        self.patients.append(patient)

    def removePatient(self, patient):
        self.patients.remove(patient)
        for doctor in self.doctors:
            if patient.doctor == str(doctor.name):
                doctor.patients.remove(patient)

    def getPatient(self, patient_id):
        for patient in self.patients:
            if (patient.id == patient_id):
                return patient

    def addPharmacy(self, ph):
        self.pharmacies.append(ph)

    def getRequest(self, r_id, doctor_id):
        for doctor in self.doctors:
            if (doctor.id == doctor_id):
                for req in doctor.appointments:
                    if (req.id == r_id):
                        return req
    def getRequestOrd(self, r_id, pharmacy_id):
        for ph in self.pharmacies:
            if (ph.id == pharmacy_id):
                for req in ph.orders:
                    if (req.id == r_id):
                        return req

    def getPharmacy(self, ph_id):
        for pharmacy in self.pharmacies:
            if pharmacy.id == ph_id:
                return pharmacy
    def removePharmacy(self, pharmacy):
        self.pharmacies.remove(pharmacy)

    def changeDoctor(self, old_doctor, new_doctor):
        copy_old = copy.copy(old_doctor.patients)  # make a copy of the patients that are from the doctor I will delete
        # I do this copy to make the for loop work, because if I delete and run the loop it will skip objects
        for patient in copy_old:
            new_doctor.patients.append(patient)
        for patient in old_doctor.patients:
            patient.doctor = new_doctor.name  # make a reference to the object doctor in the attribute of the class patient
            # If I store the object enclosure directly it leads to a circular reference error
        old_doctor.patients.clear()  # make the patients list of the doctor empty
        self.doctors.remove(old_doctor)
        session.commit()

    def cancelAppointment(self, appointment):
        for doctor in self.doctors:
            if (appointment.to_ == doctor.id):
                for patient in self.patients:
                    if (appointment.from_ == patient.id):
                        appointment.date = "cancelled"
                        appointment.time = "cancelled"
                        appointment.duration = "cancelled"
                        appointment.cost= "cancelled"
                        session.commit()

    def StatsHospital(self):
        longest = None
        sum_patients = 0
        app_cancelled= 0
        for doctor1 in self.doctors:
            sum_patients+= len(doctor1.patients)
            for appointment in doctor1.appointments:
                if appointment.date == "cancelled":
                    app_cancelled+=1
            for doctor2 in self.doctors:
                if (len(doctor2.appointments) >= len(doctor1.appointments)) :
                        if (doctor2.id != doctor1.id):
                            longest = len(doctor2.appointments)
                else:
                    longest= len(doctor1.appointments)
            av = sum_patients / len(self.doctors)
            perc_app_cancelled = (app_cancelled / sum_patients)*100

        return longest, av, perc_app_cancelled





#----------------------------------------------------------------------------------
class Patient(Base):
    __tablename__ = 'patient'
    id = Column(String, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    email = Column(String)

    def __init__(self, name, age, email):
        self.id = str(uuid.uuid4())
        self.name = name
        self.age = age
        self.email = email
        self.appointments = []
        self.appointments_request = {}
        self.appointments_approved={}
        self.doctor = None

    def __repr__(self):
        return self.name

    def bookAppointment(self, doctor, date, time, duration, cost):
        #appointment = Appointment(date, time, duration, cost)
        req = AppointmentRequest(self, doctor, date, time, duration, cost)
        #doctor.requests_ap.append(req)
        doctor.appointments.append(req)
        self.appointments.append(req)
        print(self.name, "has required an appointment with doctor ", doctor.name)
        self.appointments_request.update({req.id : datetime.datetime.now()})
        return req

    def stats(self, appointment):
        date_requested = self.appointments_request.get(str(appointment.id))
        date_approved = self.appointments_approved.get(str(appointment.id))
        wait = date_approved - date_requested
        return(f"The time between the request and the approval was: {wait}", wait)


#---------------------------------------------------------------------------------------
class Doctor(Base):
    __tablename__ = 'doctor'
    id = Column(String, primary_key=True)
    name = Column(String)
    department = Column(String)
    email = Column(String)

    def __init__(self, name, department, email):
        self.id = str(uuid.uuid4())
        self.name = name
        self.department = department
        self.email = email
        self.appointments = []
        self.patients = []
        self.orders = []
        self.orders_requested = {}
        self.orders_delivered = {}
        #self.med_received = []

    def __repr__(self):
        return self.name

    def approve(self, r, hospital):
        r.approve(hospital)

    def reject(self, r, hospital):
        r.reject(hospital)

    def addPatient(self, patient):
        self.patients.append(patient)

    def orderMedicine(self, pharmacy, cost, medicine):
        req = MedicineRequest(self, pharmacy, cost, medicine)
        self.orders.append(req)
        pharmacy.orders.append(req)
        self.orders_requested.update({req.id: datetime.datetime.now()})
        print(self.name, "has required the medicine ", req.medicine, "to the pharmacy ", pharmacy.name, "on ", req.date_time)
        return req

    def stats(self, order):
        date_requested = self.orders_requested.get(str(order.id))
        date_delivered = self.orders_delivered.get(str(order.id))
        wait = date_delivered - date_requested
        return (f"The time between the request and the delivery was: {wait}", wait)


#---------------------------------------------------------------------------------------
class Pharmacy(Base):
    __tablename__ = 'pharmacy'
    id = Column(String, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.orders = []
        #self.requests = []
        self.requests_record = {} #store the time
        #self.to_deliver = []  # orders approved but not delivered yet
        #self.delivered = []
    def __repr__(self):
        return self.name

    def approve(self, r, hospital):
        r.approve(hospital)

    def reject(self, r, hospital):
        r.reject(hospital)

    def deliverMedicine(self, order, hospital):
        order.delivered = str(datetime.datetime.now()) #Tengo que cambiar de list a str
        for doctor in hospital.doctors:
            if (doctor.id == order.from_):
                doctor.orders_delivered.update({order.id: datetime.datetime.now()})
        session.commit()


Base.metadata.create_all(engine)
#----------------------------------------------------------------------------------
class Request:
    def __init__(self, from_, to_): #all the requests start being not approved
        self.from_ = from_.id
        self.to_ = to_.id
        #self.approved = approved
        #self.id = str(uuid.uuid4())

    def __repr__(self):
        return self.id

class AppointmentRequest(Request, Base):
    __tablename__ = 'appointments'
    id = Column(String, primary_key=True)
    approved = Column(Integer, nullable=True)
    date = Column(String)
    time = Column(String)
    duration = Column(Integer)
    cost = Column(Integer)
    from_ = Column(String, ForeignKey('patient.id'), nullable=True)
    #patient_id = Column(String, ForeignKey('patient.id'), nullable=True)
    #patient = relationship("Patient", back_populates="appointments")
    to_ = Column(String, ForeignKey('doctor.id'), nullable=True)
    #doctor_id = Column(String, ForeignKey('doctor.id'), nullable=True)
    #doctor = relationship("Doctor", back_populates="appointments")

    def __init__(self, from_, to_, date, time, duration, cost):
        Request.__init__(self, from_, to_)
        #self.from_ = from_.name
        #self.to_ = to_.name
        #self.appointment = appointment
        self.date = date
        self.time = time
        self.duration = duration
        self.cost = cost
        self.id = str(uuid.uuid4())
        self.approved = 0
        #self.doctorr = None
        #self.patientt = None

    def approve(self, hospital):
        # to_ = doctor
        # from_ = patient
        for patient in hospital.patients:
            if (self.from_ == patient.id):
                for doctor in hospital.doctors:
                    if (self.to_ == doctor.id):
                        if self in doctor.appointments:
                            # delete the request for the appointment of the doctor
                            self.approved += 1
                            if patient not in doctor.patients:
                                doctor.patients.append(patient)  # add the patient to the list of patients of the doctor
                            patient.doctor = self.to_
                            for appointment in patient.appointments:
                                if self.id == appointment.id:
                                    appointment.approved = 1  # add the appointment to the patient
                                    patient.appointments_approved.update({self.id: datetime.datetime.now()})
                            for appointment in doctor.appointments:
                                if self.id == appointment.id:
                                    appointment.approved = 1
                            #doctor.appointments.append(self)

                            #self.appointment.doctorr = self.to_
                            #self.appointment.patientt = self.from_
                            print("The request of appointment from ", self.from_, "with the doctor ", self.to_,
                                  "has been approved")
                            session.commit()
                            #return self

    def reject(self, hospital):
        # to_ = doctor
        # from_ = patient
        for patient in hospital.patients:
            if (self.from_ == patient.id):
                for doctor in hospital.doctors:
                    if (self.to_ == doctor.id):
                        if self in doctor.appointments:
                            self.approved -= 1
                            print("It is not possible to confirm this appointment. Try in another time or date")
                            session.commit()


class MedicineRequest(Request, Base):
    __tablename__ = 'orders'
    id = Column(String, primary_key=True)
    approved = Column(Integer, nullable=True)
    delivered = Column(String, nullable=True)
    cost = Column(Integer)
    medicine = Column(String)
    from_ = Column(String, ForeignKey('doctor.id'), nullable=True)
    to_ = Column(String, ForeignKey('pharmacy.id'), nullable=True)

    def __init__(self, from_, to_, cost, medicine):
        Request.__init__(self, from_, to_)
        self.cost = cost
        self.medicine = medicine
        self.id = str(uuid.uuid4())
        #self.doctor = None
        #self.pharmacy = None
        self.date_time = datetime.datetime.now()
        self.approved = 0
        self.delivered = "-"

    def approve(self, hospital):
        # from_ = doctor
        # to_ = pharmacy
        for pharmacy in hospital.pharmacies:
            if (self.to_ == pharmacy.id):
                for doctor in hospital.doctors:
                    if (self.from_ == doctor.id):
                        if self in doctor.orders:
                            self.approved += 1
                            pharmacy.requests_record.update({"id" : self.id, "time": datetime.datetime.now()})
                            #pharmacy.requests.append(self)  # add the appointment to the patient
                            #doctor.orders.append(self)
                            session.commit()
                            print("The request of medicine from doctor ", self.from_, "to the pharmacy ", self.to_, "has been approved")

    def reject(self, hospital):
        for pharmacy in hospital.pharmacies:
            if (self.to_ == pharmacy.id):
                for doctor in hospital.doctors:
                    if (self.from_ == doctor.id):
                        self.approved-=1
                        session.commit()
                        print("We don't have that medicine available. You should ask in another pharmacy")

#Patient.appointments = relationship("AppointmentRequest", order_by= AppointmentRequest.id, back_populates="patient")
#Doctor.appointments = relationship("AppointmentRequest", order_by = AppointmentRequest.id, back_populates="doctor")

#-----------------------------------------------------------------------------------------------



Base.metadata.create_all(engine)

#--------------------------------------------------------------------------
#4. Create a session:
#The objectes that are added to the session are object that have to be persistence: store in the database

SessionClass = sessionmaker(bind = engine) #make the session usign the engine
session = SessionClass()

#5. Add objects to the database (to the class)
if __name__ == "__main__":
    hospital = Hospital()
    d1 = Doctor("James", "pediatrician", "jm1@gmail.com") #the id is automatically generated
    d2 = Doctor("Tom", "gynecologist", "tom@gmail.com")

    p1 = Patient("Sofia", 25, "sofio@gmail.com")
    p2 = Patient("Sam", 60, "sam3@gmail.com")

    session.add_all([p1, p2, d1, d2])
    session.add(Doctor("Henry", "pediatrician", "henry@gmail.com"))

    hospital.addDoctor(d1)
    hospital.addDoctor(d2)
    hospital.addPatient(p1)
    hospital.addPatient(p2)

    req1 = p1.bookAppointment(d1, '10-06-2022', '11:00', 30, 150)
    session.commit() #insert statement in the background
    request = req1[0]
    appoint = req1[-1]
    d1.approve(request, hospital)

    session.commit() #insert statement in the background

    session.close()