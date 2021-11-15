import datetime
import json
import re
import dateutil.parser
import pymongo
import redis

from paho.mqtt import client as mqtt_client
from cloud.settings import REDIS_HOST, REDIS_PORT, MG_HOST, MG_PORT, MG_DB_NAME, MQTT_CLIENT_CONFIG

uhf_loading_data, ae_tev_loading_data = {}, {}

sensor_redis_cli = redis.Redis(
    connection_pool=redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=5, decode_responses=True))
mg_cli = pymongo.MongoClient(f"mongodb://{MG_HOST}:{MG_PORT}/")[MG_DB_NAME]


class DataLoader:
    """
    just load data into mongodb
    """

    collection_mapping = {
        '二合一传感器': 'ae_tev',
        '特高频传感器': 'uhf',
        '温度传感器': 'temperature'
    }

    pattern = re.compile(r"/(?P<client_id>[a-zA-Z0-9]+)/subnode/(?P<sensor_id>[a-zA-Z0-9]+)/data_ctrl/property")

    def __init__(self, client_id, host="121.37.185.39", port=10883):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.client = mqtt_client.Client(self.client_id)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("#")  # 订阅消息

    @staticmethod
    def get_sensor_type(msg_dict):
        params = msg_dict.get('params', {})
        if 'TEV' in params or 'AE' in params:
            return 'ae_tev'
        elif 'Temp' in params:
            return 'temp'
        else:
            return ''

    @staticmethod
    def insert(client_id, sensor_id, sensor_type, msg_dict):
        cur_time = dateutil.parser.parse(datetime.datetime.utcnow().isoformat())
        my_col = mg_cli[sensor_type]
        my_query = {'is_new': True}
        new_values = {"$set": {"is_new": False, "update_time": cur_time}}
        my_col.update_many(my_query, new_values)
        params = msg_dict.get('params', {})
        if sensor_type == 'ae':
            params.pop('TEV')
        if sensor_type == 'tev':
            params.pop('AE')
        data = {
            'client_id': client_id,
            'sensor_id': sensor_id,
            'version': msg_dict.get('version', ''),
            'sensor_type': sensor_type,
            'params': params,
            'create_time': cur_time,
            'update_time': cur_time,
            'is_new': True,
        }
        insert_res = my_col.insert_one(data)
        if insert_res.acknowledged:
            print('插入数据成功！！！')
        else:
            print(f'{msg_dict}插入数据失败！！！')

    @staticmethod
    def on_message(client, userdata, msg):
        print(f"msg.topic:{msg.topic}")
        ret = DataLoader.pattern.match(msg.topic)
        if ret is not None:
            client_id, sensor_id = ret.groups()[0], ret.groups()[1]
            if sensor_redis_cli.sismember('client_ids', client_id):
                msg_dict = json.loads(msg.payload.decode('utf-8'))
                sensor_type = DataLoader.get_sensor_type(msg_dict)
                if sensor_type:
                    if sensor_type == 'ae_tev':
                        for sensor_type in ['ae', 'tev']:
                            DataLoader.insert(client_id, sensor_id, sensor_type, msg_dict)
                    else:
                        DataLoader.insert(client_id, sensor_id, sensor_type, msg_dict)

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        print("On Subscribed: qos = %d" % granted_qos)

    @staticmethod
    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection %s" % rc)
        else:
            print("disconnection !!!")

    def run(self):
        self.client.username_pw_set("guest", "guest")
        self.client.on_connect = DataLoader.on_connect
        self.client.on_message = DataLoader.on_message
        self.client.on_subscribe = DataLoader.on_subscribe
        self.client.on_disconnect = DataLoader.on_disconnect
        self.client.connect(self.host, self.port, 60)
        self.client.loop_forever()


subscribe_client_id = MQTT_CLIENT_CONFIG.get('subscribe_client_id', '')
host = MQTT_CLIENT_CONFIG.get('host', '')
port = MQTT_CLIENT_CONFIG.get('port', '')
data_loader = DataLoader(subscribe_client_id, host, port)

if __name__ == "__main__":
    data_loader.run()
