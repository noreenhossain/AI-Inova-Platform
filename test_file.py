import streamlit as st
import streamlit.components.v1 as stc

# File Processing Pkgs
# import pandas as pd
import docx2txt
# from PIL import Image 
from PyPDF2 import PdfReader
# import pdfplumber

def read_pdf(file):
	pdfReader = PdfReader(file)
	count = len(pdfReader.pages)
	all_page_text = ""
	for i in range(count):
		page = pdfReader.pages[i]
		all_page_text += page.extract_text()

	return all_page_text


def main():
	st.title("File Upload Tutorial")

	docx_file = st.file_uploader("Upload File",type=['txt','docx', 'pdf'])
	if st.button("Process"):
		if docx_file is not None:
			file_details = {"Filename":docx_file.name,"FileType":docx_file.type,"FileSize":docx_file.size}
			st.write(file_details)
			# Check File Type
			if docx_file.type == "text/plain":
				st.text(str(docx_file.read(),"utf-8")) # empty
				raw_text = str(docx_file.read(),"utf-8") # works with st.text and st.write,used for futher processing
				st.text((raw_text)) # Works
			elif docx_file.type == "application/pdf":
				raw_text = read_pdf(docx_file)
				st.text(type(raw_text))  
				
			elif docx_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
			# Use the right file processor ( Docx,Docx2Text,etc)
				raw_text = docx2txt.process(docx_file) # Parse in the uploadFile Class directory
				st.text(type(raw_text))




if __name__ == '__main__':
	main()


	