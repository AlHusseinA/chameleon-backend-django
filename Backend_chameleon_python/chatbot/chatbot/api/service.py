import uuid

from google.cloud.dialogflowcx_v3beta1 import QueryInput
from google.cloud.dialogflowcx_v3beta1.services.agents import AgentsClient
from google.cloud.dialogflowcx_v3beta1.services.sessions import SessionsClient
from google.cloud.dialogflowcx_v3beta1.types import session, EventInput

# [START dialogflow_detect_intent_text]
from google.oauth2 import service_account

from django.conf import settings

# all of the code below is taken from https://github.com/googleapis/python-dialogflow-cx/blob/HEAD/samples/snippets/detect_intent_texts.py
# and slightly modified

def get_client():
    # set up authentication
    project_id = "plucky-alliance-316021"
    # For more information about regionalization see https://cloud.google.com/dialogflow/cx/docs/how/region
    location_id = "europe-west2"
    # For more info on agents see https://cloud.google.com/dialogflow/cx/docs/concept/agent
    agent_id = "a6cddc05-9042-41e9-b61b-d93a3880e936"
    agent = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"


    agent_components = AgentsClient.parse_agent_path(agent)
    location_id = agent_components["location"]
    client_options = None
    if location_id != "global":
        api_endpoint = f"{location_id}-dialogflow.googleapis.com:443"
        print(f"API Endpoint: {api_endpoint}\n")
        client_options = {"api_endpoint": api_endpoint}
    # store credentials
    creds_location = f"{settings.ROOT_DIR}/chatbot/plucky.json"
    credentials = service_account.Credentials.from_service_account_file(creds_location)
    # https://googleapis.dev/python/dialogflow-cx/latest/dialogflowcx_v3/sessions.html?highlight=sessionsclient#google.cloud.dialogflowcx_v3.services.sessions.SessionsClient
    # SessionsCient creates the session in which this user (until they refresh their screen or close the window) will interact with dialogflow
    return SessionsClient(credentials=credentials, client_options=client_options), agent


def call_dialogflow(session_uuid, texts=None):
    return detect_intent_texts(session_uuid, texts=texts)


# this will buidl the json object that will be passed to dialogflo api. This will contain text_input (see detect_input_texts below)
def build_intent_query(text_input=None, event=None):
    language_code = "en"
    # if input is text (not an event on the page) then text_input == true
    # the second return is legacy from my earlier attempt to expirement with sending
    # click events to the api

    if text_input:
        return session.QueryInput(text=text_input, language_code=language_code)

    return session.QueryInput(event=event, language_code=language_code)


def detect_intent_texts(session_id, texts=None, event=None):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation."""
    #  all of the code below is taken from https://github.com/googleapis/python-dialogflow-cx/blob/HEAD/samples/snippets/detect_intent_texts.py and slightly edited

    # creates a session for the user/client with appropriate authentication + an instance of Chameleon with the same session id
    client, agent = get_client()
    session_path = f"{agent}/sessions/{session_id}"
    print(f"Session path: {session_path}\n")
    returned_message = {}

    for text in texts:
        text_input = session.TextInput(text=text)
        query_input = build_intent_query(text_input=text_input, event=event)
        request = session.DetectIntentRequest(session=session_path, query_input=query_input)
        response = client.detect_intent(request=request)

        for index, message in enumerate(response.query_result.response_messages):
            print(message.text.text)
            returned_message.update({index: message.text.text[0]})

    return returned_message


