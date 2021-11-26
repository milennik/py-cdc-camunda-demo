from pymongo import MongoClient
from pymongo.collection import ReturnDocument
from config import mongo_uri, database, outbox_collection,application_data_profile
import random
from faker import Faker
import uuid
import time
import random

fake = Faker()
NUM_RECORDS_TO_GENERATE = 1

# mongo connection data
client = MongoClient(mongo_uri)
db = client[database]


def insert(session):
    
    adp = {
        "uw_profile":[],
        "application_id":uuid.uuid4(),
        "carrier":"eflic",
        "seizure_count": random.randint(1,10)
    }
    
    db[application_data_profile].insert_one(adp, session=session)
    copy_to_outbox(payload=adp, action_type='insertApplication', session=session)
    print(f'inserted: \n {adp}')


def update(session):
    op = db[application_data_profile].find_one_and_update(
        {'carrier': "eflic"},
        {'$inc': {'anything_else': "something else 2"}},
        upsert=False,
        return_document=ReturnDocument.AFTER
    )
    if op is not None:
        copy_to_outbox(payload=op, action_type='updateApplication', session=session)
        print(f'updated: \n {op}')


def delete(session):
    op = db[application_data_profile].find_one_and_delete(
        {'carrier': "eflic"},
    )
    if op is not None:
        copy_to_outbox(payload=op, action_type='deleteApplication', session=session)
        print(f'deleted: \n {op}')


def copy_to_outbox(payload, action_type, session):
    payload['actionType'] = action_type
    # remove _id so mongo can create new one in session
    payload.pop('_id', None)
    db[outbox_collection].insert_one(payload, session=session)
    print('outbox: ', action_type)

def main():
    # events = [insert, update, delete]
    events = [insert]
    for idx in range(NUM_RECORDS_TO_GENERATE):
        for event in events:
            time.sleep(1)
            with client.start_session(causal_consistency=True) as session:
                with session.start_transaction():
                    event(session=session)


if __name__ == '__main__':
    main()
