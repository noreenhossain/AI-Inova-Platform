# Importing necessary libraries
import streamlit as st
import openai
from PyPDF2 import PdfReader

import docx2txt
import pandas as pd
from io import StringIO

st.set_page_config(layout="wide")

# Main page with 3 rows and 2 columns
st.title("GPT Deck Summarizer")

openai.api_key = "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"


def read_pdf(file):
	pdfReader = PdfReader(file)
	count = len(pdfReader.pages)
	all_page_text = ""
	for i in range(count):
		page = pdfReader.pages[i]
		all_page_text += page.extract_text()

	return all_page_text

prompt_text = """Please provide a profile of the company described in this text, including if it is public or private,​ who the founders are, its founding date, and any parent companies if possible. Next, name the key asset described in the text in the format "Name of Asset (Name of Company)". Next, describe the key asset in two paragraphs, including key information about the stage it is in, and any future milestones mentioned. Next, describe how it compares to similar assets that exist. Next, repeat description for all other assets mentioned in the text. Finally, print "Summary Complete" """
gpt_model = "gpt-4"


def main():

    document_text = ""
    docx_file = st.file_uploader("Upload File",type=['txt','docx', 'pdf'])
    if docx_file is not None:
        file_details = {"Filename":docx_file.name,"FileType":docx_file.type,"FileSize":docx_file.size}
        st.write(file_details)
        # st.session_state.output_text = "Placeholder"
        # Check File Type
        if docx_file.type == "text/plain":
            st.text(str(docx_file.read(),"utf-8")) # empty
            document_text = str(docx_file.read(),"utf-8") # works with st.text and st.write,used for futher processing
            # st.text((document_text)) # Works
        elif docx_file.type == "application/pdf":
            document_text = read_pdf(docx_file)
            # st.text(type(document_text))  
            
        elif docx_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # Use the right file processor ( Docx,Docx2Text,etc)
            document_text = docx2txt.process(docx_file) # Parse in the uploadFile Class directory
            # st.text(type(document_text))
    
    col1_1, col1_2 = st.columns([2, 3])

    with col1_1:
        
        with st.expander("Prompt", expanded=True):
                prompt_box = st.text_area("Here is the prompt to summarize a deck. Feel free to adjust the prompt if needed.", value=prompt_text)

    
    with col1_2:
        output = ""
        st.text_area("GPT Summary of Deck",
            output,
            height=500,
            key="output_text",
            placeholder="Please click \'Get GPT Summary\' to generate summary")

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

            st.session_state.output_text = response['choices'][0]['message']['content']

        st.button("Get GPT Summary", key="get_gpt_button", on_click=on_gpt_indication_click)

if __name__ == '__main__':
	main()