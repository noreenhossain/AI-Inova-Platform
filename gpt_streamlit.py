# Importing necessary libraries
import streamlit as st
import openai
from PyPDF2 import PdfReader
import pyclip
# import clipboard
import docx2txt


# broadcasting and set host for streamlit app 

st.set_page_config(layout="wide")

# Main page with 3 rows and 2 columns
st.title("S&E GPT Deck Summarizer™")

# OpenAI API Key
openai.api_key = ""

# Method to process uploaded PDFs
def read_pdf(file):
	pdfReader = PdfReader(file)
	count = len(pdfReader.pages)
	all_page_text = ""
	for i in range(count):
		page = pdfReader.pages[i]
		all_page_text += page.extract_text()

	return all_page_text

# Default prompt text that can be modified in Streamlit window
prompt_text = """Please provide a profile of the company described in this text, including if it is public or private,​ who the founders are, its founding date, and any parent companies if possible. Next, name the key asset described in the text in the format "Name of Asset (Name of Company)". Next, describe the key asset in two paragraphs, including key information about the stage it is in, and any future milestones mentioned. Next, describe how it compares to similar assets that exist. Next, repeat description for all other assets mentioned in the text. Finally, print "Summary Complete" """
# gpt_model = "gpt-4"


# Setting up the document
document_text = ""

# Add a file uploader
docx_file = st.file_uploader("Upload File",type=['txt','docx', 'pdf'])

# Checks the uploaded file and stores information about it
if docx_file is not None:
    file_details = {"Filename":docx_file.name,"FileType":docx_file.type,"FileSize":docx_file.size}
    # Confirmation that file was uploaded successfully if file details written
    st.write(file_details)
    # Check File Type
    # TXT
    if docx_file.type == "text/plain":
        st.text(str(docx_file.read(),"utf-8")) # empty
        document_text = str(docx_file.read(),"utf-8") # works with st.text and st.write,used for futher processing
    # PDF
    elif docx_file.type == "application/pdf":
        document_text = read_pdf(docx_file) 
    # DOCX
    elif docx_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    # Use the right file processor ( Docx,Docx2Text,etc)
        document_text = docx2txt.process(docx_file) # Parse in the uploadFile Class directory
        # st.text(type(document_text))

# Make Columns for Propmpt box and summary box
col1_1, col1_2 = st.columns([2, 3])

# Prompt Box
with col1_1:
    with st.expander("Prompt", expanded=True):
            prompt_box = st.text_area("Here is the prompt to summarize a deck. Feel free to adjust the prompt if needed.", height = 300, key = "prompt_box", value=prompt_text)

    def reset_prompt():
        st.session_state.prompt_box = prompt_text

    st.button("Reset Prompt Text", on_click = reset_prompt)

    gpt_model = st.selectbox(
    'Which GPT Model do you want to use?',
    ("gpt-4", 'gpt-3.5-turbo-16k'))


# Generated Summary Box
with col1_2:
    output = ""
    a = st.text_area(f"GPT Summary of Deck using the {gpt_model} model",
        output,
        height=500,
        key="output_text",
        placeholder="Please click \'Get GPT Summary\' to generate summary")

    # Function to generate GPT Response using prompt and document
    def on_gpt_indication_click():
        response = openai.ChatCompletion.create(
            model= gpt_model,
            messages=[{"role": "user", "content": f"{prompt_box}: {document_text}"}],
            temperature=0,
            # max_tokens=500,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        # return response['choices'][0]['message']['content']
        st.session_state.output_text = response['choices'][0]['message']['content']

    # Function to clear text box
    def clear_box():
        st.session_state.output_text = output

    # Make action buttons
    summary, clear = st.columns([1,1])

    # Get GPT summary and replace output with generated response
    with summary:
        st.button("Get GPT Summary", key="get_gpt_button", on_click=on_gpt_indication_click)
        
    # Clear the text in the output box
    with clear:
        if st.button("Clear Output", on_click = clear_box):
            del st.session_state.output_text
            st.session_state.output_text = "Blank"
    # Copy the text in the output box
    # Pyperclip not working with Linux!!
    # with copy:
    #     if st.button('Copy Summary Text'):
    #         pyclip.copy(a)
    #         st.success('Text copied successfully!')
  