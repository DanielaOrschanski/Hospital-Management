import datetime
import pytest
from HospitalClasses import Hospital, Doctor, Patient, Pharmacy, Request, MedicineRequest, AppointmentRequest
import time

#FIXTURES--------------------------------------------------------------------------
@pytest.fixture
def hospital():
    return Hospital()

@pytest.fixture
def d1():
    return Doctor("James", "pediatrician", "jm1@gmail.com") #the id is automatically generated

@pytest.fixture
def d2():
    return Doctor("Tom", "gynecologist", "tom@gmail.com")

@pytest.fixture
def p1():
    return Patient("Sofia", 25, "sofio@gmail.com")

@pytest.fixture
def p2():
    return Patient("Sam", 60, "sam3@gmail.com")

@pytest.fixture
def ph1():
    return Pharmacy("Sol")

@pytest.fixture
def hospital111(hospital, d1, p1, ph1):
    hospital.addDoctor(d1)
    hospital.addPatient(p1)
    hospital.addPharmacy(ph1)

#TESTS-------------------------------------------------------------------------------------------------
def test_BookingAppointments(d1, p1, hospital111):
    req1 = p1.bookAppointment(d1, '10-06-2022', '11:00', 30, 150)
    assert d1.appointments[-1] == req1
    assert p1.appointments[-1] == req1
    assert req1.approved == 0 #check that the appointment exists but it hasnt been approved

def test_ApprovingAppointment(d1, p1, hospital111, hospital):
    p1.bookAppointment(d1, '10-06-2022', '11:00', 30, 150)
    req = d1.appointments[-1]
    d1.approve(d1.appointments[-1], hospital)
    assert req.approved == 1 #the status of the appointment has changed
    assert d1.patients[-1] == p1
    assert p1.doctor == d1.id
    assert d1.appointments[-1] == req #confirm that the appointment is still stored
    assert p1.appointments[-1] == req
    assert req.from_ == p1.id
    assert req.to_ == d1.id

def test_RejectingAppointment(hospital111, d1, p1, hospital):
    req1 = p1.bookAppointment(d1, '10-06-2022', '11:00', 30, 150)
    d1.reject(req1, hospital)
    assert req1.approved == -1
    assert p1.doctor == None
    assert p1 not in d1.patients

def test_RequiringMedicine(d1, ph1, hospital111):
    req = d1.orderMedicine(ph1, 30, 'ibuprofene')
    assert req == d1.orders[-1]
    assert req in ph1.orders
    assert req.approved == 0

def test_ApprovingOrder(ph1, d1, hospital111, hospital):
    req = d1.orderMedicine(ph1, 30, 'ibuprofene')
    ph1.approve(req, hospital)
    assert ph1.orders[-1].approved == 1  # the status of the appointment has changed
    assert d1.orders[-1] == req  # confirm that the appointment is still stored
    assert ph1.orders[-1] == req
    assert req.from_ == d1.id
    assert req.to_ == ph1.id

def test_RejectingOrder(hospital111, d1, ph1, hospital):
    req1 = d1.orderMedicine(ph1, 20, "frenaler")
    ph1.reject(req1, hospital)
    assert req1.approved == -1

def test_DeliverMedicine(ph1, hospital111, d1, hospital):
    reqm1 = d1.orderMedicine(ph1, 30, 'ibuprofene')
    ph1.approve(reqm1, hospital)
    ph1.deliverMedicine(reqm1, hospital)
    assert reqm1.delivered == str(datetime.datetime.now())

def test_DeleteDoctor(hospital111, hospital, d1, d2, p1):
    d1.addPatient(p1)
    assert p1 in d1.patients
    hospital.addDoctor(d2)
    assert len(d2.patients) == 0
    hospital.changeDoctor(d1, d2)
    assert p1 not in d1.patients
    assert p1 in d2.patients

def test_cancelAppointment(hospital111, hospital, p1, d1):
    req1 = p1.bookAppointment(d1, '10-06-2022', '11:00', 30, 150)
    d1.approve(req1, hospital)
    hospital.cancelAppointment(req1)
    assert req1.date == "cancelled"
    assert req1.time == "cancelled"
    assert req1.duration == "cancelled"
    assert req1.cost == "cancelled"


def test_statsDoctor(hospital111, ph1, d1, hospital):
    req1 = d1.orderMedicine(d1, 30, 'aspirine')
    #time.sleep(2)
    ph1.approve(req1, hospital)
    ph1.deliverMedicine(req1, hospital)
    out = d1.stats(req1)
    wait = out[-1]
    assert out[0] == f"The time between the request and the delivery was: {wait}"

def test_StatsHospital(hospital, d1, d2,p1, p2, hospital111):
    hospital.addDoctor(d2)
    req1 = p1.bookAppointment(d1, '10-06-2022', '11:00', 30, 150)
    req2 = p2.bookAppointment(d1, '15-06-2022', '16:00', 30, 150)
    req3 = p1.bookAppointment(d2, '18-06-2022', '13:00', 30, 150)
    req4 = p1.bookAppointment(d1, '20-06-2022', '11:00', 30, 150)
    req5 = p1.bookAppointment(d1, '25-06-2022', '11:00', 30, 150)
    d1.approve(req1, hospital)
    d1.approve(req2, hospital)
    d2.approve(req3, hospital)
    d1.approve(req4, hospital)
    d1.approve(req5, hospital)
    hospital.cancelAppointment(req1)
    stats = hospital.StatsHospital()
    longest = stats[0]
    average= stats[1]
    percentage_app_cancelled= stats[2]

    assert longest == 4
    assert average == 1
    assert percentage_app_cancelled == (1/2)*100

def test_HospitalStatsError(hospital, d1, d2,p1, p2, hospital111):
    hospital.addDoctor(d2)
    req1 = p1.bookAppointment(d1, '10-06-2022', '11:00', 30, 150)
    req2 = p2.bookAppointment(d1, '15-06-2022', '16:00', 30, 150)
    d1.approve(req1, hospital)
    d1.approve(req2, hospital)

    with pytest.raises(ZeroDivisionError) as ex: # I expect an error because the doctor 2 doesnt have patients so the division will be done with 0
        print(hospital.StatsHospital())







