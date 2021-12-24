from confluent_kafka import Consumer, KafkaError
import json
import pandas as pd
from sqlalchemy import create_engine

settings = {
    'bootstrap.servers': '143.244.160.62:30845',
    'group.id': 'mygroup',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'earliest'}
}

c = Consumer(settings)

c.subscribe(['output-ksqldb-tweet-corona-word-count'])
engine = create_engine('postgresql://postgres:6e8e5979-25c5-44e2-ad76-7a4e8ee68c6f@174.138.108.45:5432/tweets')
try:
    while True:
        msg = c.poll(0.1)
        if msg is None:
            continue
        elif not msg.error():
            msg = json.loads(msg.value().decode('utf-8'))
            print(msg)
            df = pd.DataFrame(msg,index=[0])
            df.to_sql('corona_tweets_word_count', engine, if_exists='append', index=False)
            print('Message committed to database')

        elif msg.error().code() == KafkaError._PARTITION_EOF:
            print('End of partition reached {0}/{1}'
                  .format(msg.topic(), msg.partition()))
        else:
            print('Error occured: {0}'.format(msg.error().str()))

except KeyboardInterrupt:
    pass

finally:
    c.close()