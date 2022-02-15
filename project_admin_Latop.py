# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import csv

# Configuration details and certificate paths
clientId = "Laptop"
endpoint = "atailpsdx6e70-ats.iot.us-east-1.amazonaws.com"

rootCAFilePath = "C:/Users/Joel/Downloads/AmazonRootCA1.pem"
privateKeyFilePath = "C:/Users/Joel/Downloads/PrivateKey.key"
certFilePath = "C:/Users/Joel/Downloads/DeviceCertificate.crt"

# For certificate based connection
myMQTTClient = AWSIoTMQTTClient(clientId)

# Configurations: -
# For TLS mutual authentication
myMQTTClient.configureEndpoint(endpoint, 8883)
myMQTTClient.configureCredentials(rootCAFilePath, privateKeyFilePath, certFilePath)
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

QoS = 0
topic = "smart_security_password"
topic_username = "smart_security_username"
topic_valid = "smart_security_valid"

password = "1234"

def usernameOnMessage(client, userdata, message):
    unn = message.payload
    finalUsername = unn.decode("utf-8")
    print(finalUsername)
    json_username = json.loads(finalUsername)
    usernameReceived = json_username["username"]
    invalid = 0
    valid = 1
    with open('usernames.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        if usernameReceived in open('usernames.csv').read():
            myMQTTClient.publish(topic_valid, valid, QoS)
        else:
            myMQTTClient.publish(topic_valid, invalid, QoS)



def customOnMessage(client, userdata, message):
    userEnteredusername = message.payload
    finalUsername = userEnteredusername.decode("utf-8")
    print(finalUsername)

def validOnMessage(client, userdata, message):
    return 0

def main():
    connect_ACK = myMQTTClient.connect()
    myMQTTClient.subscribe(topic, QoS, customOnMessage)
    myMQTTClient.subscribe(topic_username, QoS, usernameOnMessage)
    myMQTTClient.subscribe(topic_valid, QoS, validOnMessage)

    password = "1234"
    myMQTTClient.publish(topic, password, QoS)

    while True:
        time.sleep(1)

    myMQTTClient.unsubscribe(topic)
    myMQTTClient.unsubscribe(topic_username)
    myMQTTClient.unsubscribe(topic_valid)
    myMQTTClient.unsubscribe(topic_sns)

    myMQTTClient.disconnect()

if __name__ == "__main__":
    main()
