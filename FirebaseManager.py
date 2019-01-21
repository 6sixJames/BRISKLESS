import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from Phidget22.Devices.TemperatureSensor import *
import time
from datetime import datetime

#used as the document id within the database.
START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def onAttachHandler(self):
    """
    This needs to be done as a 'monkey patched' event handler - not sure why.
    Some settings can be changed here
    """
    self.setDataInterval(1000)
    self.setTemperatureChangeTrigger(0.0)


def log_to_firebase(self, temperature):
    """
    This function is used as a mixin for the Phidget class - i.e. it will be used inside that class at runtime.

    :param self: parent object
    :param temperature: temp float which gets passed in by parent
    :return:
    """

    doc_ref = db.collection(START_TIME).document()
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

    # set the log to firebase mixin to run on every temp change
    BrisklessPhidget.setOnTemperatureChangeHandler(log_to_firebase)

    # launch temperature reading from Phidget
    BrisklessPhidget.openWaitForAttachment(5000)

    while True:
        time.sleep(10)
