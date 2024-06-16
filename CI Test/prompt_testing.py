
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser

def evaluation_chain(
    input_data,
    llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
    output_parser=StrOutputParser()
):
    eval_system_prompt = """You are an assistant that evaluates whether an input containing a patient transcript and related information has all required fields present and non-empty.
    The input data should include the following keys: Transcript, Summary, Issue, Issue Summary, Severity, Clinician to Contact.
    """

    eval_user_message = f"""Please evaluate the following input data to ensure all required fields are present and contain valid, non-empty data:
    Here is the data:
    [BEGIN DATA]
    ************
    Transcript: {input_data.get('Transcript', '')}
    Summary: {input_data.get('Summary', '')}
    Issue: {input_data.get('Issue', '')}
    Issue Summary: {input_data.get('Issue Summary', '')}
    Severity: {input_data.get('Severity', '')}
    Clinician to Contact: {input_data.get('Clinician to Contact', '')}
    ************
    [END DATA]

    Check if the following fields are present and contains valid, non-empty data:
    - Transcript
    - Summary
    - Issue
    - Issue Summary
    - Severity
    - Clinician to Contact


    Respond with 'Y' if all fields are present and non-empty, 'N' if any field is missing, empty, or if the field contains the keyword "Invalid".
    """

    eval_prompt = ChatPromptTemplate.from_messages([
        ("system", eval_system_prompt),
        ("human", eval_user_message),
    ])

    return eval_prompt | llm | output_parser
