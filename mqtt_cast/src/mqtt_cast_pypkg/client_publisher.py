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

# 作用：本地调试
# TODO: 后续可能要写成一个状态机，方便整个流程调试
# TODO: 在本地建立一个broker进行调试


class MqttClient(object):
    def __init__(self):
        rospy.init_node("mqtt_client_node",
                        disable_signals=True, anonymous=True)
        self.debug = bool(rospy.get_param("~mqtt_debug"))
        self.deviceId = "nicsefc-robot-001"
        self.clientId = "nicsefc-robot-001"

        self.seq_num = 0
        # for the mqtt server's cmd message
        self.server_cmd_queue = queue.Queue()

        # -------------------------------init data slot----------------------------
        # TODO: 目前是随意设置的
        '''
        # 状态类型：10=待机,20=到达取货点,30=柜门已打开,40=已经拿到货物,50=到达 楼门口,60=到电梯口,70=到达指定楼层,80=到达指定位置,90=卸货完成,100=已 到待机,110=异常
        self.status_type = 10
        self.health_status: int = 0  # 0/1   abnormal/normal
        self.voltage: float = 80  # TODO:百分比，80%
        self.outdoor_pose: list = [0.0, 0.0, 0.0]  # outdoor x,y,yaw
        self.indoor_pose: list = [0, 0, 0]         # indoor x,y,yaw
        self.floor_num = 4
        self.orderId = "12345678"
        '''

        # ------------------------------init mqtt client----------------------------------
        self.client = mqtt.Client(self.clientId)
        self.client.username_pw_set("admin", "public")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.mqtt_connection_init = False

        # broker.mqttdashboard.com  test.mosquitto.org   iot.eclipse.org  broker.emqx.io
        self.client.connect(
            str(rospy.get_param("~broker_ip", '127.0.0.1')), keepalive=20)
        self.client.loop_start()
        while self.mqtt_connection_init == False:
            print("[INFO]: Waiting for mqtt connection init ... ")
            time.sleep(1)

    def SendMsg(self):
        msg = {
            "seqId": str(self.seq_num),
            "actionTime": int(CurrentTimeMillis()),
            "deviceId": str(self.deviceId),
            "indoorX": self.GetLocX(),
            "indoorY": self.GetLocY(),
            "statusCode": self.GetStatusCode()
        }
        self.seq_num += 1
        try:
            publish_result = self.client.publish(topic="/"+self.deviceId+"/robot_info",
                                                 payload=json.dumps(msg),
                                                 qos=1)
            publish_result.wait_for_publish()
        except Exception as e:
            if self.debug:
                print(
                    f'[ERROR]: raise exception \'{e}\' in function \'SendMSg\'')

    def GetStatusCode(self):
        return 0

    def GetLocX(self):
        return "0"

    def GetLocY(self):
        return "0"

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

    def on_disconnect(self, client, userdata, rc):
        print("[WARNING]: MQTT client disconnect from the broker !")

    def on_message(self, client, userdata, message):
        print(message.topic + " " + str(message.payload))
