import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("Conectado con resultado: " + str(rc))
    client.subscribe("Máquina/M17/estado/CambioDeMolde")
    client.subscribe("Máquina/M17/estado/EnPreparación")
    client.subscribe("Máquina/M17/estado/Ciclo")
    client.subscribe("Máquina/M17/estado/EnProducción")
    client.subscribe("Máquina/M17/estado/EnLimpiezaLubricación")
    client.subscribe("Máquina/M17/estado/EnPreventivo")
    client.subscribe("Máquina/M17/estado/EnCorrectivo")


def on_message(client, userdata, msg):
    print(msg.topic+" "+msg.payload.decode())


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.loop_forever()
