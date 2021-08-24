from kafka import KafkaConsumer
import json

if __name__ == '__main__':

    consumer = KafkaConsumer('sink', group_id='my-group', bootstrap_servers=['127.0.0.1:9092'], value_deserializer=json.loads)

    for m in consumer:
        print(m)