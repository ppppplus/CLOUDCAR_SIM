#!/usr/bin/python3
# -*- coding:utf-8 -*-
from mqtt_cast_pypkg.client_publisher import MqttClient
import rospy
import time

if __name__ == '__main__':
    client = MqttClient()
    debug = bool(rospy.get_param("~mqtt_debug", default=True))
    while not rospy.is_shutdown():
        client.SendMsg()
        print(f'[DEBUG]:  pub status message to broker ! ')
        time.sleep(1)
