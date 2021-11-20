from pymongo import MongoClient
from config import mongo_uri, database, outbox_collection
import json
import uuid
from camunda.client.engine_client import EngineClient


# mongo connection data
client = MongoClient(mongo_uri)
db = client[database]
outbox_collection = db[outbox_collection]

def listen_for_large_orders():
    # Change stream pipeline
    pipeline = [
        {'$match': {'fullDocument.amount': {'$gte':1000}}}
    ]
    try:

        x=0
        print('listening...')
        with open('resume_token.json') as json_file:
            resume_token = json.load(json_file)
        # for document in outbox_collection.watch(pipeline=pipeline):
        # for document in outbox_collection.watch(start_after=resume_token):
        for document in outbox_collection.watch():
            x=x+1
            print(x)
            print(f"\n=== LARGE AMOUNT {document['fullDocument']['actionType']} ===\n")
            print(document['fullDocument'])

            client = EngineClient("http://localhost:8080/engine-rest")
            resp_json = client.start_process(process_key="my_process1", variables={"intVar": "1", "strVar": "hello"},
                                 tenant_id="", business_key=str(uuid.uuid1()))

            print(resp_json)

            with open('resume_token.json', 'w') as outfile:
                json.dump(document['_id'], outfile)

    except KeyboardInterrupt:
        keyboard_shutdown()

if __name__ == '__main__':
    listen_for_large_orders()

# Generic 105-key PC (intl.)
