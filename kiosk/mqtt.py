import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("connect.." + str(rc))
    if rc == 0:
        client.subscribe("test")
    else:
        print("연결실패...")

def on_message(client, userdata, message):
    try:
        print("메시지 수신완료 ")
        value = message.payload.decode("utf-8")
        print("현재 전송받은 값은:"+value+"입니다.")
        if(value == '0'):
            print("노년 남성입니다.")
        elif(value == '1'):    
            print("노년 여성입니다.")
        elif(value == '2'):    
            print("일반성인 남성입니다.")
        elif(value == '3'):    
            print("일반성인 여성입니다.")
        else:
            print("잘못된 값입니다.")
    except Exception as e:
        print("에러발생", e)

    finally:
        pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("18.142.203.134", 1883, 60)
client.loop_forever()