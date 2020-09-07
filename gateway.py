'''
PLC_SLOT
 - IP Address Only (``10.20.30.100``) - Use for a ControlLogix PLC is in slot 0 or if connecting to a CompactLogix or Micro800 PLC.
 - IP Address/Slot (``10.20.30.100/1``) - (ControlLogix) if PLC is not in slot 0
 - CIP Routing Path (``1.2.3.4/backplane/2/enet/6.7.8.9/backplane/0``) - Use for more complex routing.
 - MQTT Message format is Json {"name": "tagName", "type": "DINT", "value": 123}
'''

import os
import threading
import paho.mqtt.client as mqtt
import json
import time
from pycomm3 import LogixDriver


class NewThread:
    id = 0
    idStop = False
    idThread = threading.Thread


def load_file(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
        return data


def on_connect(mqttc, obj, flags, rc):
    qos = 0
    print("rc: " + str(rc))
    for each_tag in TAG_LIST:
        topic_path = CONTROL_BASE_TOPIC + "/" + each_tag["name"]
        MQTT_CLIENT.subscribe(topic_path, qos)
        print('subscribed to: ' + topic_path)


def on_message(mqttc, obj, msg):
    print('message received...')
    print('preparing to send to PLC...')
    mqtt_message = str(msg.payload)[2:-1]
    #print(mqtt_message)
    msg_data = json.loads(mqtt_message)
    # new_message = json.loads(mqtt_message)
    # print(msg.topic + " " + str(msg.qos) + ", " + mqtt_message)
    print(msg_data["name"])
    print(int(msg_data["value"]))
    PLC_CLIENT.write((msg_data["name"], int(msg_data["value"])))


def on_publish(mqttc, obj, mid):
    if False:
        print("Published: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


def init_plc_monitor_thread():  # creates the workout thread
    MQTT_CLIENT.on_message = on_message
    MQTT_CLIENT.on_connect = on_connect
    MQTT_CLIENT.on_publish = on_publish
    MQTT_CLIENT.on_subscribe = on_subscribe
    MQTT_CLIENT.connect(BROKER_ADDRESS, BROKER_PORT, 60)
    MQTT_CLIENT.subscribe(STATUS_BASE_TOPIC, 0)
    PLC_MONITOR.idStop = False
    PLC_MONITOR.id = 101
    PLC_MONITOR.idThread = threading.Thread(target=start_plc_thread,
                                            args=(PLC_MONITOR.id,
                                                  lambda: PLC_MONITOR.idStop))
    PLC_MONITOR.idThread.start()


def halt_plc_monitor_thread():  # requests an end to the workout
    try:
        PLC_MONITOR.id = 101
        PLC_MONITOR.idStop = True
        PLC_MONITOR.idThread.join()
    except Exception as e:
        print(e)  # if there is an error attempting the workout then here....


def start_plc_thread(my_id, terminate):
    """
    This thread polls the PLC on regular intervals based on the poll time
    """
    prev_status = []
    #print(PLC_CLIENT.get_tag_list())
    while not terminate():  # wait while this interval completes
        new_status = []
        changed_values = []
        for each_tag in TAG_LIST:
            new_tag = {"name": PLC_CLIENT.read(each_tag["name"]).tag,
                       "value": PLC_CLIENT.read(each_tag["name"]).value,
                       "type": PLC_CLIENT.read(each_tag["name"]).type}
            new_status.append(new_tag)
        for i in new_status:
            if i not in prev_status:
                changed_values.append(i)
        if changed_values:
            for each_changed_tag in changed_values:
                topic_path = STATUS_BASE_TOPIC + "/" + each_changed_tag["name"]
                tag_data = {"name": each_changed_tag["name"],
                           "value": each_changed_tag["value"],
                           "type": each_changed_tag["type"]}
                #print(topic_path)
                #print(json.dumps(tag_data))
                MQTT_CLIENT.publish(topic_path, json.dumps(tag_data))
        prev_status = []
        prev_status = new_status
        time.sleep(POLL_TIME / 1000)  #


settings = load_file("settings.json")

POLL_TIME = int(settings["poll_time"])
PLC_ADDRESS = str(settings["plc_address"])
PLC_SLOT = str(settings["plc_slot"])
PLC_PATH_STRING = str(PLC_ADDRESS) + '/' + str(PLC_SLOT)
#print(PLC_PATH_STRING)
PLC_CLIENT = LogixDriver(PLC_PATH_STRING)
PLC_MONITOR = NewThread

MQTT_CLIENT = mqtt.Client()
BROKER_ADDRESS = str(settings["broker_address"])
BROKER_PORT = int(settings["broker_port"])
CONTROL_BASE_TOPIC = str(settings["control_topic"])  # communications to the PLC
STATUS_BASE_TOPIC = str(settings["status_topic"])  # communications from the PLC

TAG_LIST = settings["tags"]
'''
logixMQTTgateway/control/TestTag
'''

init_plc_monitor_thread()
#MQTT_CLIENT.loop_start()
MQTT_CLIENT.connect_async(BROKER_ADDRESS, BROKER_PORT, 60)
MQTT_CLIENT.loop_start()
