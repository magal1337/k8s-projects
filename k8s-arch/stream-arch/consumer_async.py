from confluent_kafka import Consumer, KafkaError
import json
import pandas as pd
from sqlalchemy import create_engine
import asyncio
import asyncpg

settings = {
    'bootstrap.servers': '143.244.160.62:30845',
    'group.id': 'mygroupasync5',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'earliest'}
}
loop = asyncio.get_event_loop()
c = Consumer(settings)

c.subscribe(['output-ksqldb-tweet-corona-word-count'])
#engine = create_engine('postgresql://postgres:6e8e5979-25c5-44e2-ad76-7a4e8ee68c6f@174.138.108.45:5432/tweets')
async def run(msg:dict):
    conn = await asyncpg.connect(user='postgres', password='6e8e5979-25c5-44e2-ad76-7a4e8ee68c6f',
                                 database='tweets', host='174.138.108.45',port=5432)
    values = await conn.fetch(f"""
    INSERT INTO public.corona_tweets_word_count ("TWEET_ID","WORD_COUNT") VALUES ('{0}', '{1}');""".format(msg['TWEET_ID'], msg['WORD_COUNT']))
    
    await conn.close()
tasks = []
try:
    while True:
        msg = c.poll(0.1)
        if msg is None:
            continue
        elif not msg.error():
            msg = json.loads(msg.value().decode('utf-8'))
            tasks.append(loop.create_task(run(msg)))
            print(f"appending msg {msg} to task")
            if len(tasks) > 20:
                loop.run_until_complete(asyncio.wait(tasks))
                tasks.clear()
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
    loop.close()