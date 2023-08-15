# Importing necessary libraries
import streamlit as st
import openai

openai.api_key = "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"

st.set_page_config(layout="wide")

# Main page with 3 rows and 2 columns
st.title("Claude LLM Parsing")

with st.expander("Prompt", expanded=True):
    prompt_text = st.text_area("Prompt", value="Summarize this text: ")

col1_1, col1_2 = st.columns([3, 2])

with col1_1:
    indications_text = st.text_area(
        "Text", 
        "",
        key="text",
        height=220)
    
with col1_2:
    output = ""
    indications_output = st.text_area("Summary",
        output,
        height=220,
        key="output_text",
        placeholder="Click 'GPT Summary' to update")

    def on_gpt_indication_click():
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "user", "content": f"{prompt_text}: {indications_text}"}],
            temperature=0,
            max_tokens=500,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        output = response['choices'][0]['message']['content']

        # Way to access Streamlit settion's "output_text" key
        st.session_state.output_text = output

    st.button("Get GPT Summary", key="get_gpt_button", on_click=on_gpt_indication_click)