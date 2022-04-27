import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def subscribe():

    client = mqtt.Client("test")
    # 设置用户名和密码
    client.username_pw_set("admin", "public")
    client.on_connect = on_connect
    client.on_message = on_message
    #client.on_disconnect = on_disconnect
    # 连接 IP port keepalive
    client.connect('172.16.0.94', 1883, 600)
    # 订阅的 topic
    client.subscribe("/#", qos=0)
    client.loop_forever()


def publish():
    client = mqtt.Client()
    # 设置用户名和密码
    client.username_pw_set("admin", "public")
    client.on_connect = on_connect
    client.on_message = on_message
    # 连接 IP port keepalive
    client.connect('172.16.0.94', 1883, 600)
    # 发布 topic 内容
    client.publish('test', payload='have a seventh test', qos=0)
    client.publish('test', payload='have a eighth test', qos=0)


# publish()
subscribe()
