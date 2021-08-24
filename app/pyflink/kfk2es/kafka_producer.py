from json import dumps
from faker import Faker
from kafka import KafkaProducer
from time import sleep

bootstrap_servers = ['127.0.0.1:9092']
topic = "test"
fake = Faker()
fake_num = 20

def write_data():
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda x: dumps(x).encode('utf-8')
    )
    # for i in range(fake_num):
    #     cur_data = {
    #         "ip": fake.ipv4(),
    #         "port": fake.port_number(),
    #         "country": fake.country(),
    #         "city": fake.city(),
    #     }
    #     print(cur_data)
    cur_data = {
        "message": "<5>time:2020-04-21 07:14:27;danger_degree:5;breaking_sighn:0;event:[50575]向日葵远程控制软件连接服务器;src_addr:10.30.3.178;src_port:33668;dst_addr:47.111.183.245;dst_port:443;user:;smt_user:;proto:SSL"
    }
    producer.send(topic, value=cur_data)

if __name__ == '__main__':
    write_data()