from flask import Flask, request, jsonify
from src.create_vector_db import CreateCollection  
from pymongo import MongoClient
import pandas as pd
import config
import json
import os
import logging
from datetime import datetime
from flask_cors import CORS
from src.app_helper import MongoManager, history_manager,PrepareVectorData
from src.app_helper import AddressProcessor, PropertyAnalyzer,NumpyEncoder, get_location_info_prompt

from src.gpt_agents import GPTAgents, ResponseChecker
# initiate Gpt prompts
agent = GPTAgents()


# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object('config')
CORS(app)

db_manager = MongoManager(config.MONGO_CLIENT, config.MONGO_DB)

# get_personal_details decprated
@app.route('/get_personal_details', methods=['POST'])
def get_personal_details():
    try:
        data = request.get_json()
        api_key = request.json.get('api_key')

        if 'query' not in data:
            return jsonify({'error': 'Query parameter is missing'}), 400

        user_query = data['query']
        query_result = agent.run_query_gpt(user_query)
        return jsonify({"success": True, "prompt": query_result})
    except Exception as e:
        return jsonify({"error": str(e),"success":False})
    

@app.route('/get_prompt', methods=['POST'])
def get_initial_prompt():
    try:
        final_prompt = db_manager.get_insights()
        # GPT response
        query_result = agent.run_initial_prompt(final_prompt)
        query_result_dict = json.loads(query_result)
        query_result = query_result_dict.get('initial_prompt')
        logging.info(query_result)
        return jsonify({"success": True, "prompt": query_result})
    except Exception as e:
        return jsonify({"error": str(e),"success":False})

@app.route('/get_query', methods=['POST'])
def get_query():
    try:
        data = request.get_json()
        logging.info(data)
        api_key = request.json.get('api_key')

        if 'query' not in data:
            return jsonify({'error': 'Query parameter is missing'}), 400

        user_query = data['query']
        user_messages = data['message']

        history_messages = history_manager(user_messages, user_query)


        # Vector DB manager
        collection_manager = CreateCollection() # remove the parameter to get vector collection just initiate it
        db_collection = collection_manager.get_collection('vector_' + api_key)  # get vector collection TODO: add parameter to get collection

        metadata = []
        catagory,answer, chroma_prompt, where_clause = agent.get_filters(user_query,history_messages,function=True)
        logging.info("CATAGORY: %s", catagory)
        # this will decide class of the query as well
        if catagory == "info":
            logging.info("/n -------------------info------------------- /n")
            data_df = db_manager.get_data_df(api_key)
            checker_agent = ResponseChecker()
            answer = checker_agent.info(chroma_prompt,data_df)
            logging.info(answer)
            logging.info("/n -------------------info------------------- /n")
        elif catagory == "residential" or catagory == "commercial":
            if where_clause is not None or chroma_prompt != "" or chroma_prompt is not None:
                result, metadata = agent.filter_query(db_collection,chroma_prompt, where_clause)
                answer = agent.responce_checker(catagory,chroma_prompt,result,answer)
        else:
            metadata = []
        if chroma_prompt is None:
            metadata = []
        logging.info('\n ------------------------------------ \n')
        logging.info(answer)
        logging.info(metadata)
        logging.info('\n ------------------------------------ \n')

        return jsonify({"success": True, "answer": answer, "result": metadata})
    except Exception as e:
        return jsonify({"error": str(e), "success": False})


# TODO: move it to the create_vector_db.py
def create_and_insert_vector_db(csv_file_path, vector_collection_name,type):
        vector_df = PrepareVectorData(csv_file_path, type) # prepare vector with metadata
        collection_manager = CreateCollection() # create vector collection
        try:
            sentence_csv = vector_df.transform_to_vector_df()
            logging.info(sentence_csv)
            collection_manager.db_collection(vector_collection_name,True, sentence_csv)
            logging.info("Vector DB created and filled with data")
        except Exception as e:
            logging.info(e)
            raise Exception("Vector DB not created and filled with data")


# TODO: Add commercial properties and residential_properties data support
@app.route('/insert_data', methods=['POST'])
def insert_data():
    try:
        csv_file_path = request.json.get('csv_file_path')
        api_key = request.json.get('api_key')
        type = request.json.get('type')
        logging.info(api_key)

        if not csv_file_path:
            return jsonify({"error": "CSV file path not provided"}), 400
        logging.info(csv_file_path)

        # Create collection and insert data
        collection_name = f"Table_{api_key}"
        db_manager.create_collection_and_insert_data( collection_name,csv_file_path,type)

        
        vector_collection_name = f"vector_{api_key}"
        create_and_insert_vector_db(csv_file_path, vector_collection_name,type)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e),"success":False})
    



if __name__ == '__main__':
    app.run(host = config.HOST, debug=config.DEBUG, port=config.PORT) # server will run on port 5000 