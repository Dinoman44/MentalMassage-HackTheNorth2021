import os
import dialogflow
from google.api_core.exceptions import InvalidArgument

# Configuration

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'apikey.json'

DIALOGFLOW_PROJECT_ID = 'hackthenorth-rwlo'
DIALOGFLOW_LANGUAGE_CODE = 'en'
SESSION_ID = 'me'

session_client = dialogflow.SessionsClient()
session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)

# Module for query and response
def ChatBot(text_to_be_analyzed):
    text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise

    temp = []

    for i in response.query_result.fulfillment_messages:
	    temp.append(i.text.text[0])

    return(temp)
