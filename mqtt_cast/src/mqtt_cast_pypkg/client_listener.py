#!/usr/bin/python3
# -*- coding:utf-8 -*-
import rosnode
import rostopic
import rospy
from geometry_msgs.msg import TwistStamped, Twist
from rospy.core import rospyinfo

import paho.mqtt.client as mqtt
from datetime import datetime
from threading import Thread
from .utils import *

import time
import copy
import random
import json
import os
import queue
import subprocess

# 作用：本地调试
# TODO: 后续可能要写成一个状态机，方便整个流程调试
# TODO: 在本地建立一个broker进行调试


class MqttClient(object):
    def __init__(self):
        rospy.init_node("mqtt_client_node",
                        disable_signals=True, anonymous=True)
        self.debug = bool(rospy.get_param("~mqtt_debug"))
        self.deviceId = "nicsefc-robot-001"
        self.clientId = "nicsefc-robot-001-sub"
        self.topic_name = "/robot_cmd"
        self.robot_name = "robot"
        self.domain_id = 2
        self.seq_num = 0

        # ------------------------------init mqtt client----------------------------------
        self.client = mqtt.Client(self.clientId)
        self.client.username_pw_set("admin", "public")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.msg_queue = queue.Queue()
        self.msg_last = None
        self.mqtt_connection_init = False

        # broker.mqttdashboard.com  test.mosquitto.org   iot.eclipse.org  broker.emqx.io
        self.client.connect(
            str(rospy.get_param("~broker_ip", '127.0.0.1')), 1883, keepalive=20)
        # self.client.connect('172.16.0.94', 1883, 600)
        # self.client.subscribe(
        #     self.productKey+"/"+self.deviceId+"/"+"adp/indoor/health_check", qos=0)
        # self.client.subscribe(self.productKey+"/" +
        #                       self.deviceId+"/"+"adp/indoor/status", qos=0)
        self.client.loop_start()
        while self.mqtt_connection_init == False:
            print("[INFO]: Waiting for mqtt connection init ... ")
            time.sleep(1)

        # self.client.loop_forever()

    def MsgProcess(self):
        # 获取mqtt message传来的参数，发送给ros（service形式）
        try:
            if self.msg_last == None:
                message = self.msg_queue.get()
                self.msg_last = message
                # print("Get new command")
            else:
                message = self.msg_last
                # print("Dont get new command, copy last message")
            start_deviceId = message["start_device"]
            car_name = message["car_name"]
            cb_index = self.DeviceInGroup(start_deviceId)
            if cb_index != -1:
                self.robot_name = "robot_"+str(cb_index)
                print("This robot is called:", self.robot_name)
                self.RobotInit()

        except Exception as e:
            if self.debug:
                print("[ERROR]: error in msgprocess:", e)

    def RobotInit(self):
        os.system(
            "gnome-terminal -x /home/nics/cloud_car/ros_bridge/ros_bridge_ws/src/ros1_bridge/script/test.sh "+str(self.domain_id))
        self.client.loop_stop()
        rospy.signal_shutdown("Local listener closed!")

    def DeviceInGroup(self, start_deviceId):
        device_list = start_deviceId.split()
        try:
            index = device_list.index(self.deviceId)
            print('Found this device in start group!Index:', index)
            return index
        except ValueError:
            print("This device was not called")
            return -1

    def GetStatusCode(self):
        return 0

    def on_connect(self, client, userdata, flags, rc):
        cases = {0: "Connection successful",
                    1: "Connection refused - incorrect protocol version",
                    2: "Connection refused - invalid client identifier",
                    3: "Connection refused - server unavailable",
                    4: "Connection refused - bad username or password",
                    5: "Connection refused - not authorised"}
        print("[INFO]: Connection returned result: "+cases[rc])
        if rc == 0:
            self.mqtt_connection_init = True
            self.client.subscribe(self.topic_name, qos=0)

    def on_disconnect(self, client, userdata, rc):
        print("[WARNING]: MQTT client disconnect from the broker !")

    def on_message(self, client, userdata, message):
        if message.topic == "/robot_cmd":
            try:
                info_message = json.loads(message.payload)
                self.msg_queue.put(info_message)
                self.MsgProcess()
                if self.debug:
                    print(f'[DEBUG]: Receive info_message .')
                    print(f'[DEBUG]: cmd details are \n {info_message}')
            except Exception as e:
                print(
                    f'[ERROR]: raise exception \'{e}\' in function \'on_message\'')
        else:
            try:
                undefined_message = json.loads(message.payload)
                if self.debug:
                    print(
                        f'[DEBUG]: Receive undefined message: {message.topic} .')
                    print(
                        f'[DEBUG]: undefined message details are \n {undefined_message}')
            except Exception as e:
                print(
                    f'[ERROR]: raise exception \'{e}\' in function \'on_message\'')
