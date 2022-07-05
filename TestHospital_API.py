#Testing through the API: simulate that the paramters in the API is being filled
import json
import requests
import pytest
import datetime

@pytest.fixture
def baseURL():
    return("http://127.0.0.1:7890/")

@pytest.fixture
def HospitalWithOnePatient(baseURL):
    requests.post(baseURL + "/patient", {"name": "Sam Robinson", "age": 25, "email": "srobinson@gmail.com"})
    response = requests.get(baseURL+"/patients")
    return response.content

def test_Patients(baseURL):
    patient = requests.post(baseURL + "/patient", {"name": "Zoe Harrison", "age": 65, "email": "harryzoe@gmail.com"})
    response = requests.get(baseURL + "/patients")
    jo = json.loads(response.content)
    p = jo.get('Zoe Harrison')
    assert p[1] == 65 #age

@pytest.fixture
def HospitalWithOneDoctor(baseURL):
    requests.post(baseURL + "/doctor", {"name": "Dr. Orschanski", "email": "orschanski@gmail.com", "department": "pediatrician"})
    response = requests.get(baseURL+"/doctors")
    return response.content

def test_Doctors(HospitalWithOneDoctor):
    jo = json.loads(HospitalWithOneDoctor)
    p = jo.get("Dr. Orschanski")
    assert (len(jo) == 1)
    assert p[1] == "pediatrician"

def test_BookingApp(HospitalWithOneDoctor, HospitalWithOnePatient, baseURL):
    jo = json.loads(HospitalWithOnePatient)
    p = jo.get("Sam Robinson")
    patient_id = p[0]

    jo2 = json.loads(HospitalWithOneDoctor)
    d = jo2.get("Dr. Orschanski")
    doctor_id = d[0]

    response = requests.post(baseURL + f"/patients/{patient_id}/bookApointment/{doctor_id}", {"info": "20-05-2022, 11:00, 30, 100"})
    jo3 = json.loads(response.content)
    assert jo3['message'] == "Sam Robinson has requested an appointment on 20-05-2022 with the doctor Dr. Orschanski"
    response4 = requests.get(baseURL + "/doctors")
    jo4 = json.loads(response4.content)
    doc = jo4.get("Dr. Orschanski")
    assert len(doc[3]) == 1

def test_ApproveAppointment(baseURL, HospitalWithOneDoctor, HospitalWithOnePatient ):
    response1 = requests.get(baseURL+ "/doctors")
    jo1 = json.loads(response1.content)
    doc = jo1.get("Dr. Orschanski")
    doctor_id = doc[0]

    jo = json.loads(HospitalWithOnePatient)
    p = jo.get("Sam Robinson")
    patient_id = p[0]

    response2 = requests.post(baseURL + f"/patients/{patient_id}/bookApointment/{doctor_id}",
                             {"info": "20-05-2022, 11:00, 30, 100"})
    jo2 = json.loads(response2.content)

    response3 = requests.get(baseURL + "/doctors")
    jo3 = json.loads(response3.content)
    docc = jo3.get("Dr. Orschanski")
    request_id = docc[3].get(patient_id)

    response4 = requests.get(baseURL + "/patients")
    jo4 = json.loads(response4.content)
    patt = jo4.get("Sam Robinson")
    assert len(patt[4]) == 1 #appointments requested

    response5 = requests.post(baseURL + f"/doctors/{doctor_id}/ApproveAppointment/{request_id}")
    jo5 = json.loads(response5.content)

    response6 = requests.get(baseURL + "/patients")
    jo6 = json.loads(response6.content)
    pattt = jo6.get("Sam Robinson")
    assert len(pattt[5]) == 1 #appointments approved


def test_DeleteDoctor(baseURL, HospitalWithOneDoctor):
    requests.post(baseURL + "/doctor", {"name": "Dr. Smith", "department": "ginecologist", "email": "smith@gmail.com"})
    response1 = requests.get(baseURL + "/doctors")
    jo = json.loads(response1.content)
    # I am counting on having 4 doctors created by other tests done previously
    assert len(jo) == 5
    doctor_id = jo[-1]['id']
    requests.delete(baseURL + f"/doctor/{doctor_id}")
    response2 = requests.get(baseURL + "/doctors")
    jo1 = json.loads(response2.content)
    assert len(jo1) == 4

@pytest.fixture
def HospitalWithOnePharmacy(baseURL):
    requests.post(baseURL + "/pharmacy", {"name": "Vienna's Pharmacy"})
    response = requests.get(baseURL+"/pharmacies")
    return response.content

def test_Pharmacies(HospitalWithOnePharmacy):
    jo = json.loads(HospitalWithOnePharmacy)
    print(jo)
    assert (len(jo) == 1)
    assert jo[0]["name"] == "Vienna's Pharmacy"

def test_DeletePatient(baseURL, HospitalWithOnePatient):
    requests.post(baseURL + "/patient", {"name": "Steve Harrison", "age": 50, "email": "sharrison@gmail.com"})
    response1 = requests.get(baseURL + "/patients")
    jo = json.loads(response1.content)
    # I am counting on having 1 doctors created by other tests done previously
    assert len(jo) == 4
    patient_id = jo[-1]['id']
    requests.delete(baseURL + f"/patient/{patient_id}")
    response2 = requests.get(baseURL + "/patients")
    jo1 = json.loads(response2.content)
    assert len(jo1) == 3

def test_DeletePharmacy(baseURL, HospitalWithOnePharmacy):
    requests.post(baseURL + "/pharmacy", {"name": "Graz's Pharmacy"})
    response1 = requests.get(baseURL + "/pharmacies")
    jo = json.loads(response1.content)
    # I am counting on having 1 doctors created by other tests done previously
    assert len(jo) == 3
    pharmacy_id = jo[-1]['id']
    requests.delete(baseURL + f"/pharmacy/{pharmacy_id}")
    response2 = requests.get(baseURL + "/pharmacies")
    jo1 = json.loads(response2.content)
    assert len(jo1) == 2


def test_OrderMedicine(HospitalWithOneDoctor, HospitalWithOnePharmacy, baseURL):
    response1 = requests.get(baseURL+ "/pharmacies")
    jo1 = json.loads(response1.content)
    pharmacy_id = jo1[-1]['id']

    response2 = requests.get(baseURL + "/doctors")
    jo2 = json.loads(response2.content)
    doctor_id = jo2[-1]['id']

    response3 = requests.post(baseURL + f"/doctors/{doctor_id}/orderMedicine/{pharmacy_id}", {"info": "100, ibuprofene"})
    jo3 = json.loads(response3.content)
    assert jo3 == "Dr. Orschanski has made an order to Vienna's Pharmacy"
    response4 = requests.get(baseURL + "/doctors")
    jo4 = json.loads(response4.content)
    assert len(jo4[-1]["requests_med"]) == 1

    response5 = requests.get(baseURL + "/pharmacies")
    jo5 = json.loads(response5.content)
    assert len(jo5[-1]["requests"]) == 1

def test_ApproveOrder(baseURL, HospitalWithOneDoctor, HospitalWithOnePharmacy):
    response1 = requests.get(baseURL+ "/pharmacies")
    jo1 = json.loads(response1.content)
    #i am counting on having a request of medicine in the second doctor
    request_id = jo1[-2]['requests'][-1]['id']
    pharmacy_id = jo1[-2]['id']
    assert len(jo1[-2]['requests']) == 1

    response2 = requests.post(baseURL + f"/pharmacies/{pharmacy_id}/ApproveOrder/{request_id}")
    jo2 = json.loads(response2.content)

    response3 = requests.get(baseURL + "/pharmacies")
    jo3 = json.loads(response3.content)
    assert len(jo3[-2]['requests']) == 0
    assert len(jo3[-1]['to_deliver'])== 1

def test_deliverMedicine(HospitalWithOnePharmacy, baseURL):
    response1 = requests.get(baseURL+ "/pharmacies")
    jo1 = json.loads(response1.content)
    pharmacy_id = jo1[-2]['id']
    order_id = jo1[-2]['to_deliver'][-1]['id']

    response2 = requests.post(baseURL + f"/pharmacies/{pharmacy_id}/deliverMedicine/{order_id}")
    jo2 = json.loads(response2.content)
    response3 = requests.get(baseURL + "/pharmacies")
    jo3 = json.loads(response3.content)
    assert len(jo1[-2]['to_deliver']) == 0

#def test_changeDoctor(HospitalWithOneDoctor, baseURL, d2):



