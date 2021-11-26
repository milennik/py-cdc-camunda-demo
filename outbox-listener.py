from pymongo import MongoClient
from config import mongo_uri, database, outbox_collection
import json
import uuid
from camunda.client.engine_client import EngineClient


client = MongoClient(mongo_uri)
db = client[database]
outbox_collection = db[outbox_collection]

def listen_for_apps():
    try:
        print('listening...')

        with open('resume_token.json') as json_file:
            resume_token = json.load(json_file)

        for document in outbox_collection.watch(start_after=resume_token):
            print(f"\n=== NEW OUTBOX RECORD: {document['fullDocument']['actionType']} ===\n")

            print(document['fullDocument'])
            
            adp = {
                "uw_profile":[],
                "application_id":str(document['fullDocument']['application_id']),
                "carrier":document['fullDocument']['carrier'],
                "seizure_count":document['fullDocument']['seizure_count']
            }

            client = EngineClient("http://localhost:8080/engine-rest")

            resp_json = client.start_process(process_key="wf_demo", variables=adp, tenant_id="", business_key=str(uuid.uuid1()))

            print(resp_json)

            with open('resume_token.json', 'w') as outfile:
                json.dump(document['_id'], outfile)

    except KeyboardInterrupt:
        keyboard_shutdown()

if __name__ == '__main__':
    listen_for_apps()