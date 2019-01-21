import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from Phidget22.Devices.TemperatureSensor import *
import time
from datetime import datetime

setup = input("do you want to set up? y/n")

if setup.lower() == "y":
    # used as the document id within the database.
    USER_NAME = input("Enter Username: ")
    SMOKER = input("What kind of smoker do you have? ")
    MEAT = input("What cut of meat are you cooking? ")
elif setup.lower() == "n":
    USER_NAME = "GALLAGHER_NICK"
    SMOKER = "Weber 22"
    MEAT = "Brisket"


def onAttachHandler(self):
    """
    This needs to be done as a 'monkey patched' event handler - not sure why.
    Some settings can be changed here
    """
    self.setDataInterval(1000)
    self.setTemperatureChangeTrigger(0.0)


def create_new_cook():
    """
    Initializes a new document in the firebase store, adds 'Cook level' data - i.e. Meat and Smoker Info.
    :return:
    """
    cook_doc = db.collection(USER_NAME).document()
    print(f"Created new cook for user {USER_NAME} with cook id:{cook_doc.id}")

    cook_doc = db.collection(USER_NAME).document(cook_doc.id)
    cook_doc.set({"smoker": SMOKER, "meat": MEAT})

    return cook_doc.id


def log_to_firebase(self, temperature):
    """
    This function is used as a mixin for the Phidget class - i.e. it will be used inside that class at runtime.

    :param self: parent object
    :param temperature: temp float which gets passed in by parent
    :return:
    """

    doc_ref = db.collection(USER_NAME).document(cook_id).collection("data").document()
    print(f"temperature {datetime.now()}---> {temperature}")
    doc_ref.set({"timestamp": datetime.now(), "temp": temperature})


def configure_phidget(serial=542_616, hub=0, channel=0):
    """

    :param serial: Serial Number as int
    :param hub: Is this connected to a hub? 1:Yes, 0:No
    :param channel: Channel 0 is Thermocouple. 1 is Board.
    :return: configured phidget
    """
    ch = TemperatureSensor()
    ch.setDeviceSerialNumber(serial)
    ch.setHubPort(hub)
    ch.setChannel(channel)
    ch.setOnAttachHandler(onAttachHandler)
    return ch


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
    BrisklessPhidget = configure_phidget()

    # db variable is used to log to firebase, despite not being explicitly passed.
    db = connect_to_firebase("briskless_firebase_auth.json")

    # set up doc id for cook
    cook_id = create_new_cook()

    # set the log to firebase mixin to run on every temp change
    BrisklessPhidget.setOnTemperatureChangeHandler(log_to_firebase)

    # launch temperature reading from Phidget
    BrisklessPhidget.openWaitForAttachment(5000)

    while True:
        time.sleep(10)
