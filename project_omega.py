import serial
import datetime

# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
from datetime import date

# Configuration details and certificate paths
clientId = "Omega_A366"
endpoint = "atailpsdx6e70-ats.iot.us-east-1.amazonaws.com"
rootCAFilePath = "/IoT/Lab8/certs/AmazonRootCA1.pem"
privateKeyFilePath = "/IoT/Lab8/certs/PrivateKey.key"
certFilePath = "/IoT/Lab8/certs/DeviceCertificate.crt"

myMQTTClient = AWSIoTMQTTClient(clientId)

myMQTTClient.configureEndpoint(endpoint, 8883)

myMQTTClient.configureCredentials(rootCAFilePath, privateKeyFilePath, certFilePath)

myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec


def send_command(ser, command):
    ser.write(command.encode())


topic = "smart_security_password"
topic_username = "smart_security_username"
topic_valid = "smart_security_valid"
topic_sns = "OmegaA366/alerts"


def serial_port():
    ser = serial.Serial(
        port='/dev/ttyS1', \
        baudrate=9600, \
        parity=serial.PARITY_NONE, \
        stopbits=serial.STOPBITS_ONE, \
        bytesize=serial.EIGHTBITS, \
        timeout=None)
    print("Connected to: " + ser.portstr)
    return ser


def check_ack(ser, check_door):
    print(check_door)
    time.sleep(1)
    ct = datetime.datetime.now()
    print("Unlocked at:-", ct)


QoS = 0


def customCallback(client, userdata, message):
    print(str(message.topic) + ": " + str(message.payload))


def customOnMessage(client, userdata, message):
    adminSetPassword = message.payload
    global password
    password = adminSetPassword.decode("utf-8")

    print("Enter Username: ")
    userEnteredUsername = input()
    payload = {"username": userEnteredUsername}

    payload = json.dumps(payload)
    myMQTTClient.publish(topic_username, payload, QoS)


def usernameOnMessage(client, userdata, message):
    username = message.payload
    userEnteredUsername = username.decode("utf-8")
    time.sleep(1)
    print("Your username is: " + userEnteredUsername)


def sendSnsOnMessage(client, userdata, message):
    return 0


def validOnMessage(client, userdata, message):
    valid = message.payload

    validUsername = valid.decode("utf-8")

    ser = serial_port()
    if (validUsername == "1"):
        print("Username is Valid")
        time.sleep(1)
        counter = 0
        while (1):
            print("Enter Password:")
            time.sleep(1)
            userEnteredPassword = input()
            if (userEnteredPassword == password):
                print("Unlocking the Door...")
                send_command(ser, "DOOR")
                recd_ack = ser.readline().decode('utf-8')
                check_ack(ser, recd_ack)
                break
            elif (userEnteredPassword != password):
                print("Wrong Password")
                print("\n")

                time.sleep(1)
                counter = counter + 1
                if (counter < 3):
                    print("Enter the Correct Password")
                    print("\n")
                    time.sleep(1)

                elif (counter == 3):
                    print("Incorrect password entered thrice")
                    print("Contact admin")
                    payload = {"sms": 1, "email": 1, "information": "User entered wrong password thrice"}

                    payload = json.dumps(payload)

                    myMQTTClient.publish(topic_sns, payload, QoS)

    else:
        print("Username Invalid")
        print("Enter Username: ")
        userEnteredUsername = input()
        payload = {"username": userEnteredUsername}
        payload = json.dumps(payload)
        myMQTTClient.publish(topic_username, payload, QoS)


def main():
    try:
        connect_ACK = myMQTTClient.connect()
        myMQTTClient.subscribe(topic, QoS, customOnMessage)
        myMQTTClient.subscribe(topic_username, QoS, usernameOnMessage)
        myMQTTClient.subscribe(topic_valid, QoS, validOnMessage)
        myMQTTClient.subscribe(topic_sns, QoS, sendSnsOnMessage)

        while True:
            time.sleep(1)

        myMQTTClient.unsubscribe(topic)
        myMQTTClient.unsubscribe(topic_username)
        myMQTTClient.unsubscribe(topic_valid)
        myMQTTClient.unsubscribe(topic_sns)
        myMQTTClient.disconnect()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()