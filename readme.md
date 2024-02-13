# Description of the Project
This Project provides an Flask API of Real Estate Website Chatbot which allows the user to Search for the  property required and our Chatbot will provide top 3 best suitable results out of all the data from the Website.

## Basic Commands to follow:
1. Install Virtual Environment in Python:-
For installing virtual environment in python use the following command:

- Windows- ```pip install virtualenv```

- Linux- ```sudo apt install python3-venv```

2. Create Virtual Environment for Python:-
For creating virtual environment in Python use the following command:

- Windows- ```python -m venv virtual_environment_name```
- Linux- ```virtualenv my_project```

3. Activate the Virtual Environment:-
To activate the virtual environment in Python use the following command:

- Windows- ```virtual_environment_name\Scripts\activate```
- Linux- ```source .venv/bin/activate```

4. Install Dependencies:-
For Installing dependencies of the project install the requirements.txt file by using the following command: ```pip install -r requirements.txt```

## Flow of the Project
In the app.py file, We have 3 endpoints of the Flask APIs which are:

1. Insert Data
- end point:	/insert_data
- method:	POST
- payload: 	{
                	"csv_file_path" :"",
                	"api_key": "",
            	}

Insert Data takes the CSV File And API Key and store the data of the CSV File in the MongoDB with the table name as "Table" + API Key.
Also, It further converts the Data of that CSV file into Viable Sentences and creates another CSV File which is further Stored in a Chroma Vector DB stored locally with the table name as "Vector" + API Key.

2. Get Personal Details
- end point:	/get_personal_details
- method:	POST
- payload: 	{
                	"query" :"",
                	"api_key": "",
            	}

Get Personal Details will fetch the "Name" and "E-mail" of the user only if the User allow us to do so.

3. Get Query
- end point:	/get_query
- method:	POST
- payload: 	{
                	"query" :"",
                	"api_key": "",
            	}

Get Query will take the User Query and find the Top 3 best suitable records for the User within the data specified by using the ChatGpt Openai API Key.

**_NOTE:_**  The full functionality is implemented in ChatBot by using LLM with RAG application in chatbot this is just part showcasing the flask API implementation of the project.