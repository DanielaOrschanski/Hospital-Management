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
    requests.post(baseURL + "/patient", {"name": "Zoe Harrison", "age": 65, "email": "harryzoe@gmail.com"})
    jo = requests.get(baseURL + "/patients")
    assert jo[-1]["name"] == "Sam Robinson"
###########################3 NO ME FUNCIONA

@pytest.fixture
def HospitalWithOneDoctor(baseURL):
    requests.post(baseURL + "/doctor", {"name": "Dr. Orschanski", "email": "orschanski@gmail.com", "department": "pediatrician"})
    response = requests.get(baseURL+"/doctors")
    return response.content

def test_Doctors(HospitalWithOneDoctor):
    jo = json.loads(HospitalWithOneDoctor)
    print(jo)
    assert (len(jo) == 1)
    assert jo[0]["name"] == "Dr. Orschanski"

def test_BookingApp(HospitalWithOneDoctor, HospitalWithOnePatient, baseURL):
    response1 = requests.get(baseURL+ "/patients")
    jo1 = json.loads(response1.content)
    patient_id = jo1[-1]['id']
    assert jo1[-1]["name"] == "Sam Robinson"

    response2 = requests.get(baseURL + "/doctors")
    jo2 = json.loads(response2.content)
    doctor_id = jo2[-1]['id']
    assert jo2[-1]["name"] == "Dr. Orschanski"

    response3 = requests.post(baseURL + f"/patients/{patient_id}/bookApointment/{doctor_id}", {"info": "20-05-2022, 11:00, 30, 100"})
    jo3 = json.loads(response3.content)
    assert jo3 == "Sam Robinson has requested an appointment on 20-05-2022 with the doctor Dr. Orschanski"
    response4 = requests.get(baseURL + "/doctors")
    jo4 = json.loads(response4.content)
    assert len(jo4[-1]["requests_ap"]) == 1

def test_ApproveAppointment(baseURL, HospitalWithOneDoctor ):
    response1 = requests.get(baseURL+ "/doctors")
    jo1 = json.loads(response1.content)
    #i am counting on having a request of appointment in the second doctor
    request_id = jo1[1]['requests_ap'][-1]['id']
    doctor_id = jo1[1]['id']
    assert len(jo1[1]['requests_ap']) == 1

    response2 = requests.post(baseURL + f"/doctors/{doctor_id}/ApproveAppointment/{request_id}")
    jo2 = json.loads(response2.content)

    response3 = requests.get(baseURL + "/doctors")
    jo3 = json.loads(response3.content)
    assert len(jo3[-1]['requests_ap']) == 0


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


