#!/usr/bin/python3
# -*- coding:utf-8 -*-
from mqtt_cast_pypkg.client_listener import MqttClient
import rospy
import time

if __name__ == '__main__':
    client = MqttClient()
    while not rospy.is_shutdown():
        time.sleep(1)
    # client.GetMsg()
