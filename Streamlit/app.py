import os
import pprint
import yaml

import streamlit as st
from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, load_prompt
from langchain_core.output_parsers.json import SimpleJsonOutputParser 

import warnings
warnings.filterwarnings("ignore")

# Load YAML configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

active_api = config["api"]["active"]
openai_api_key = config["api"]["keys"]["openai"]
google_api_key = config["api"]["keys"]["google"]
model_name_openai = config["models"]["openai"]
model_name_google = config["models"]["google"]

st.title('Emergency Response: Ambulance Call Summary and Classification\n')
input_text = st.text_input("Enter Input")

# Prompt templates

CALL_CENTRE_PROMPT = """ 

    Role: As a Language Model Assistant in an ambulance healthcare setting, your role is to assist with predicting call categories by accurately analyzing patient call transcripts to expedite the triage process.
        Vision:  You are extracting key information based on the Patient transcripts.
        Mission: Provide concise, relevant, and clear summaries of patient issues based on the patient transcripts, ensuring that they are classified appropriately and directed to the correct team for immediate attention. 

        While answering, for Severity Levels, you can choose a severity based on the context below:

        Low Severity:
            - Genito-Urinary conditions
            - Dental problem
            - Failed contraception
            - Palliative Care
            - Suicidal
        Medium Severity:
            - Level 2 interfacility transfer
            - Acute coronary syndrome
            - Refused Ambulance disposition
            - Potential Broken Arm/Leg
            - Covid symptoms with respiratory distress
        High Severity:
            - Major Blood Loss
            - Fitting now
            - Unconsciousness
            - Anaphylaxis
            - Cardiac arrest
            
        Provide the output in JSON format with the following keys:
            - Issue: (string) - Brief description of the patient's concern.
            - Issue Summary: (string, less than 20 words) - Concise overview of the problem.
            - Severity: ( Low , Medium , High ) - Urgency of the patient's situation.
            - Clinician to Contact: (general, support, technical) - If the transcript contains 3 or more “Not Sure” Keywords or “I don’t know” In it then output “Clinician to Contact Patient”
        
        Note: Before answering a question, ensure that the provided transcript is actually a dialogue. If not, then output "Invalid" for all keys.

        Transcript:
        {Transcript}

    """

SUMMARIZATION_PROMPT = """
    Please summarize the following text, capturing the key points and main concerns expressed:

    {Text}

    Make sure to include relevant details, such as symptoms, background information, current situations, and any specific requests or questions posed.
    """

# Set the active API key and model name based on the selected API
if active_api == "Gemini":
    os.environ['GOOGLE_API_KEY'] = google_api_key
    model_name = model_name_google
else:
    os.environ['OPENAI_API_KEY'] = openai_api_key
    model_name = model_name_openai

# # Display the active API key and model name for demonstration purposes
# st.write(f"Active API: {active_api}")
# if active_api == "Gemini":
#     st.write("API Key:", os.getenv('GOOGLE_API_KEY'))
# else:
#     st.write("API Key:", os.getenv('OPENAI_API_KEY'))
# st.write("Model Name:", model_name)


class DataProcessor:

    def __init__(self, active_api, model_name, SUMMARIZATION_PROMPT, CALL_CENTRE_PROMPT):
        self.summarization_prompt = PromptTemplate(
            template=SUMMARIZATION_PROMPT, input_variables=["Text"]
        )
        self.classifier_prompt = PromptTemplate(
            template=CALL_CENTRE_PROMPT, input_variables=["Transcript"]
        )
        self.active_api = active_api
        self.model_name = model_name

    def process_input(self, input_data):
        # Initialize the gemini-pro model
        try:
            if self.active_api =="Gemini":
                llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0)
                llm_json = ChatGoogleGenerativeAI(model=self.model_name, temperature=0, model_kwargs={'response_format': {"type": "json_object"}})

            if self.active_api == "OpenAI":
                llm = ChatOpenAI(model=self.model_name, temperature=0)
                llm_json = ChatOpenAI(model=self.model_name, temperature=0, model_kwargs={'response_format': {"type": "json_object"}})
            
            # Create the classifier and summary chains
            classifier_chain = self.classifier_prompt | llm_json | SimpleJsonOutputParser()
            classifier_result = classifier_chain.invoke(input_data)
            
            summary_chain = self.summarization_prompt | llm
            summary_result = summary_chain.invoke(input_data).content
            
            # Structure the results
            result = {
                "Transcript": input_data,
                "Summary": summary_result,
                "Issue": classifier_result['Issue'],
                "Issue Summary": classifier_result['Issue Summary'],
                "Severity": classifier_result['Severity'],
                "Clinician to Contact": classifier_result['Clinician to Contact']
            }
        
            return result

        except Exception as e:
            st.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            return None
    
processor = DataProcessor(active_api, model_name, SUMMARIZATION_PROMPT, CALL_CENTRE_PROMPT)

if input_text:
    st.write(processor.process_input(input_text))


# To run: streamlit run <filename.py> --server.port 8080