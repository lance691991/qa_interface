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
        "message": "<5>time:2020-05-10 12:30:34;danger_degree:1;breaking_sighn:1;event:[50083]RDP远程桌面服务终端服务用户登录;src_addr:10.10.253.14;src_port:52563;dst_addr:10.50.10.240;dst_port:3389;user:;smt_user:;proto:T_120"
    }
    datas = [cur_data for i in range(5)]
    print(datas)
    producer.send(topic, value=datas)

if __name__ == '__main__':
    write_data()