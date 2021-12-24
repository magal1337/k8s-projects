from confluent_kafka import Producer
import uuid
myuuid = uuid.uuid4()
p = Producer({'bootstrap.servers': '167.172.155.179:31408'})
p.produce('target-address', key= str(myuuid), value='this is a test')
p.flush(30)