
import os
import pprint

from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import PromptTemplate
from langchain_core.prompts import PromptTemplate, load_prompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import SimpleJsonOutputParser 
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

# Parameters

CALL_PROMPT_FILE_NAME: str = "CALL_PROMPT.yaml"
CALL_SUMMARIZATION_PROMPT_FILENAME: str = "SUMMARIZATION_PROMPT.yaml"
DEFAULT_OPENAI_MODEL_NAME: str =   "gpt-3.5-turbo"
#"gpt-4-turbo"


# Prompts

CALL_PROMPT = """ 

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
    
    Note: Before answering a question, ensure that the provided transcript is related to a reporting an issue or a similar scenario and not anything else apart from this. If not, then output 'Invalid' for all keys.

    Transcript:
    {Transcript}

"""

SUMMARIZATION_PROMPT = \
"""Please summarize the following text, capturing the key points and main concerns expressed in less than 10 words:

{Transcript}

Make sure to include relevant details, such as symptoms, background information, current situations, and any specific requests or questions posed.
"""


# Helper Functions

def save_prompt(template: str, input_variables: list, file_name: str):
    """
    Save a prompt template to a file and then load it back.

    Args:
        template (str): The template string for the prompt.
        input_variables (list): List of input variables used in the template.
        file_name (str): The name of the file to save the prompt template to.

    """
    prompt = PromptTemplate(
        template=template,
        input_variables=input_variables,
    )

    prompt.save(file_name)
    print(f"Prompt template saved to {file_name}")
    
    return 0


save_prompt(CALL_PROMPT, [], CALL_PROMPT_FILE_NAME)
save_prompt(SUMMARIZATION_PROMPT, [], CALL_SUMMARIZATION_PROMPT_FILENAME)


class CallDataProcessor:

    def __init__(self, model_name, summarization_prompt_path, classifier_prompt_path):
        self.summarization_prompt = load_prompt(summarization_prompt_path)
        self.classifier_prompt = load_prompt(classifier_prompt_path)
        self.model_name = model_name 

    def process_input(self, input_data):
        try:

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
            print(f"An error occurred: {e}")
            return None
classifier_prompt_path= CALL_PROMPT_FILE_NAME
summarization_prompt_path = CALL_SUMMARIZATION_PROMPT_FILENAME

processor = CallDataProcessor(DEFAULT_OPENAI_MODEL_NAME, summarization_prompt_path, classifier_prompt_path)


# Use as Example

# input_text = "A woman at the library collapsed and isn't breathing. We need an ambulance right away!"
# processor.process_input(input_text)
