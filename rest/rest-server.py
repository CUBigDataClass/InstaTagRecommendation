##
from flask import Flask, request, Response, jsonify
import platform
import io, os, sys
import pika, redis
import hashlib
import json
import pickle
#from PIL import Image
# import google.auth
# import google.oauth2.service_account as service_account
# from google.oauth2.service_account import Credentials
# from google.cloud import vision
# from google.cloud import storage
import uuid
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from functools import reduce
from datetime import datetime
import time
import pika
import re
import pandas as pd

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "hvhvgcgc675765bhbj"  # Change this!
jwt = JWTManager(app)

# credential_path = "keyFile-credentials.json"
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
print("Connecting to rabbitmq({})".format(rabbitMQHost))

###############################################################
#               Neerab's Redis code start                     #
###############################################################
from collections import defaultdict
redisHost = os.getenv("REDIS_HOST") or "localhost"
db = redis.Redis(host=redisHost, db=1)  
print("Connecting to redis({})".format(redisHost))
json_file_names = os.listdir('metadata')

# Remove the 5 char .json file ending to isolate hashtag name
hashtags = [hashtag[:-5] for hashtag in json_file_names]

# remove '.DS_', '.ipynb_checkp'
non_hashtags = ['.DS_', '.ipynb_checkp']
for non_hashtag in non_hashtags:
    try:
        hashtags.remove(non_hashtag)
    except:
        pass # If we can't remove it, it's already gone

# convert hashtag metadata into dataframe
hashtag_metadata = []
for hashtag in hashtags: 
    hashtag_metadata.append(pd.read_json(f'metadata/{hashtag}.json'))
hashtag_metadata = reduce(lambda x, y: pd.concat([x, y]), hashtag_metadata)
pd.DataFrame.reset_index(hashtag_metadata, drop=True, inplace=True)
hashtag_metadata.tail()

#### store the tag data in redis, so that we can use it as a cache.
def store_tag_data(hashtags):
    tag_recommender = {}
    #print(hashtag_metadata)
    for hashtag in hashtags:
        df = hashtag_metadata.loc[hashtag_metadata['search_hashtag'] == hashtag]
        hash_tags = defaultdict(int)
        for tags in df['hashtags']:
            for tag in tags:
                hash_tags[tag] += 1
        tag_recommender[hashtag] = sorted(hash_tags.items(), key=lambda item: item[1], reverse=True)[:15]
    #print(tag_recommender)
    return tag_recommender

def store_tag_redis(db):
    tag_recommender = store_tag_data(hashtags)
    #print(tag_recommender)
    ### Push the data into redis so, that we can take hashtags from cache ####
    #### push the username and password and activites into redis cache
    for hashtag in hashtags:
        db.set(hashtag,pickle.dumps(tag_recommender[hashtag]))
###############################################################
#               Neerab's Redis code end                       #
###############################################################


def enqueueDataToLogsExchange(message,messageType):
    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')

    infoKey = f"{platform.node()}.rest.info"
    debugKey = f"{platform.node()}.rest.debug"

    if messageType == "info":
        key = infoKey
    elif messageType == "debug":
        key = debugKey

    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key='logs', body=json.dumps(message))

    print(" [x] Sent %r:%r" % (key, message))

    rabbitMQChannel.close()
    rabbitMQ.close()

class enqueueWorker(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.onResponse,
            auto_ack=True)
    
    def onResponse(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    # Producer is rest-server and sending data to RabbitMQ Queue 'toWorkerQueue' ie Consumer is worker-server
    def enqueueDataToWorker(self,message):
        self.response = None
        self.corr_id = str(uuid.uuid4())    
        self.channel.basic_publish(
            exchange='', routing_key='toWorkerQueue',properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ), 
            body=json.dumps(message))
        while self.response is None:
            self.connection.process_data_events()
        #print(self.response)        
        return str(self.response.decode('utf-8'))
        #return Response(response=json.dumps(self.response), status=200, mimetype="application/json")
        #print(" [x] Sent %r:%r" % ('toWorker', message))


@app.route('/api/upload/captionimage', methods=['POST'])
def handle_captionform():
    # Adding code for rest handling - Trail
    print("###############################################################")
    print("#               Redis Code called                             #")
    print("###############################################################")

    store_tag_redis(db)
    hashtag = "travel"
    details = pickle.loads(db.get(hashtag))

    import re
    recommendation = []
    print(details)
    for tag in details:
        recommendation.append(tag[0])
    print(json.dumps(recommendation))
    return json.dumps(recommendation)

    try:
        print(" Inside Caption API Upload ")
        enqueueDataToLogsExchange('Call to api /api/upload/captionimage','info')
        print(request.files['file'])
        file = request.files['file']
 
        # dataToWorker = enqueueWorker()
        # response1 = dataToWorker.enqueueDataToWorker(file)
        # print(response1)
        # billvalue = re.sub('[^\d\.]', '',response1)
        # response = {'bill_value':str(billvalue)}
       
    
        # client = storage.Client()
        # BUCKET_NAME = 'projectexpensegenerator'
        # bucket = client.get_bucket(BUCKET_NAME)
        # destination_blob_name = name2
        # blob1 = bucket.blob(destination_blob_name)
        # blob1.upload_from_filename(name2)
 
        data = {'user_details':'abc'}
        
        dataToWorker = enqueueWorker()
        response1 = dataToWorker.enqueueDataToWorker(data) #queue
        print(response1)
  
        response = "worked succesfully"
        return Response(response, status=200, mimetype="application/json")

    except Exception as e:
        print("Something went wrong" + str(e))
        enqueueDataToLogsExchange('Error occured in api /api/upload/captionimage','info')
        return Response(response="Something went wrong!", status=500, mimetype="application/json")

@app.route('/api/upload/tagimage', methods=['GET'])
def handle_tagform():
    try:
        print(" Inside Tag API Upload ")
        enqueueDataToLogsExchange('Call to api /api/upload/tagimage','info')
        print(request.files['file'])
        file = request.files['file']
 
        # dataToWorker = enqueueWorker()
        # response1 = dataToWorker.enqueueDataToWorker(file)
        # print(response1)
        # billvalue = re.sub('[^\d\.]', '',response1)
        # response = {'bill_value':str(billvalue)}
       
    
        # client = storage.Client()
        # BUCKET_NAME = 'projectexpensegenerator'
        # bucket = client.get_bucket(BUCKET_NAME)
        # destination_blob_name = name2
        # blob1 = bucket.blob(destination_blob_name)
        # blob1.upload_from_filename(name2)
 
        data = {'user_tag':'Tagabc'}
        
        dataToWorker = enqueueWorker()
        response1 = dataToWorker.enqueueDataToWorker(data) #queue
        print(response1)
  
        response = "worked succesfully"
        return Response(response, status=200, mimetype="application/json")

    except Exception as e:
        print("Something went wrong" + str(e))
        enqueueDataToLogsExchange('Error occured in api /api/upload/tagimage','info')
        return Response(response="Something went wrong!", status=500, mimetype="application/json")

@app.route('/api/auth/getpdf', methods=['GET'])
def get_pdf():
    #data = request.get_json()
    print("--Inside GETPdf API-")
    enqueueDataToLogsExchange('Call to api /api/auth/getpdf','info')
    response = "getpdf api worked succesfully"
    
    return Response(response, status=200, mimetype="application/json")


@app.route('/api/auth/getexpenses', methods=['GET'])
def get_expenses():
    print("-Inside Get expenses API-")

    enqueueDataToLogsExchange('Call to api /api/auth/getexpenses','info')

    response = "getexpenses api worked successfully"
    
    return Response(response, status=200, mimetype="application/json")



# start flask app
app.run(host="0.0.0.0", port=5000,debug=True)
