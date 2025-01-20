# ACH Assist Agent POC v1.2
# Originally called SWIFT RAG POC

import os
from typing import Optional
import requests
import streamlit as st

from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_API_URL = os.getenv("BASE_API_URL")
LANGFLOW_ID = os.getenv("LANGFLOW_ID_AI_LAB")
APPLICATION_TOKEN = os.getenv("APPLICATION_TOKEN_AI_LAB")
ENDPOINT = os.getenv("ENDPOINT_ACH_ASSIST")
TITLE = "ACH Assist"

TWEAKS = {
  "ChatInput-f8de8": {},
  "Prompt-SfS5T": {},
  "ChatOutput-yfFep": {},
  "OpenAIModel-MD2cM": {}
}

st.title(f":blue[{TITLE}]")

def generate_response(input_text):
    for chunk in run_flow(
        message=input_text,
        endpoint=ENDPOINT,
        application_token=APPLICATION_TOKEN,
        tweaks=TWEAKS,
    ):
        yield chunk

def run_flow(
        message: str,
        endpoint: str,
        output_type: str = "chat",
        input_type: str = "chat",
        tweaks: Optional[dict] = None,
        application_token: Optional[str] = None
) -> dict:
    """
    Run a flow with a given message.

    :param message: The message to send to the flow
    :param endpoint: The Flow ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}

    response = requests.post(api_url, json=payload, headers=headers)
    yield response.json()["outputs"][0]["outputs"][0]["results"]["message"]["text"]

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Any question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Show a spinner while waiting for the streamed response
        with st.spinner("Searching for the document..."):
            try:
                response = generate_response(prompt)
                answer = st.write_stream(response)    # To display previous chat, this needs to be write_stream
                # answer = st.write(response)             # This won't display previous chat.
            except Exception as e:
                answer = "I faced a technical difficulty. Could you please ask again?"
                st.write(f"{answer}")
                # For debug
                # st.write("Error: ", str(e))

    st.session_state.messages.append({"role": "assistant", "content": answer})
