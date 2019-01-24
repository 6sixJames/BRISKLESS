import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from Phidget22.Devices.TemperatureSensor import *
import time
from datetime import datetime


def ms_since_epoch():
    """
    This is used to calculate seconds in ms since 1.1.1970, which is the way HighCharts expects to recieve datetime.
    :return: Milliseconds since January 1, 1970.
    """
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)


def get_custom_notes():
    """
    Loop for asking for user to enter additional metrics they would like to track.
    :return: List of [{key:data},....]
    """
    notes = []
    while input("additional notes? y/n").lower() == "y":
        key = input("What do you want to note")
        data = input("What is the value associate with this note?")
        notes.append({key: data})
    return notes


def onAttachHandler(self):
    """
    This needs to be done as a 'monkey patched' event handler - not sure why.
    this gets passed into the Phidget class, and is treated as Phidget.onAttachHandler at runtime.
    Some settings can be changed here
    """
    self.setDataInterval(5000)
    self.setTemperatureChangeTrigger(0.0)


def create_new_cook():
    """
    Initializes firebase document under USER_NAME collection.
    :return: The ID of initialized firebase doc
    """
    cook_doc = db.collection(USER_NAME).document()
    print(f"Created new cook for user {USER_NAME} with cook id:{cook_doc.id}")

    cook_doc = db.collection(USER_NAME).document(cook_doc.id)
    cook_doc.set({"smoker": SMOKER, "meat": MEAT})

    for note in NOTES:
        cook_doc.set(note)

    return cook_doc.id


def log_to_firebase(self, temperature):
    """
    This function is used as a mixin for the Phidget class - i.e. it will be used inside that class at runtime.

    :param self: parent object
    :param temperature: temp float which gets passed in by parent
    :return:
    """

    doc_ref = db.collection(USER_NAME).document(cook_id).collection("data").document()
    print(f"temperature {ms_since_epoch()}---> {temperature}")
    doc_ref.set({"name": ms_since_epoch(), "y": temperature, "x": ms_since_epoch()})


def phidget_thermocouple_launch(serial=542_616, hub=0, channel=0):
    """

    :param serial: Serial Number as int
    :param hub: Is this connected to a hub? 1:Yes, 0:No
    :param channel: Channel 0 is Thermocouple. 1 is Board.
    :return: configured phidget
    """
    PhidgetTempSensor = TemperatureSensor()
    PhidgetTempSensor.setDeviceSerialNumber(serial)
    PhidgetTempSensor.setHubPort(hub)
    PhidgetTempSensor.setChannel(channel)
    PhidgetTempSensor.setOnAttachHandler(onAttachHandler)
    return PhidgetTempSensor


def connect_to_firebase(path_to_json_creds):
    """
    connects to firebase cloud db
    :param path_to_json_creds: the filepath to the json credentials retrieved from the firebase dashboard
    :return: an authorized db
    """
    cred = credentials.Certificate(path_to_json_creds)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db


if __name__ == "__main__":
    # Boot loop example - runs set up and begins logging to firebase.

    setup = input("do you want to set up? y/n")

    if setup.lower() == "y":
        # used as the document id within the database.
        USER_NAME = input("Enter Username: ")
        SMOKER = input("What kind of smoker do you have? ")
        MEAT = input("What cut of meat are you cooking? ")
        NOTES = get_custom_notes()

    elif setup.lower() == "n":
        USER_NAME = "GALLAGHER_NICK"
        SMOKER = "Weber 22"
        MEAT = "Brisket"
        NOTES = []

    BrisklessPhidget = phidget_thermocouple_launch()

    # db variable is used to log to firebase, despite not being explicitly passed.
    # handled as variable within scope as work around for passing into log_to_firebase which is a monkey patched method.
    db = connect_to_firebase("briskless_firebase_auth.json")

    # set up doc id for cook
    cook_id = create_new_cook()
    print("cook created")
    # set the log to firebase mixin to run on every temp change
    BrisklessPhidget.setOnTemperatureChangeHandler(log_to_firebase)
    print("logging added")
    # launch temperature reading from Phidget
    BrisklessPhidget.openWaitForAttachment(20000)

    while True:
        time.sleep(10)
