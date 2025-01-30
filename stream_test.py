import streamlit as st
import time

def simple_generator():
    for i in range(5):
        yield f"Chunk {i}\n"
        time.sleep(1)

st.title("Stream Test")

stream = simple_generator()
response = st.write_stream(stream)
st.write("Done streaming.")
