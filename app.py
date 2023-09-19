import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

import time
import os
import io, random, base64

from pyresparser import ResumeParser
from pdfminer.high_level import extract_text
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags

st.set_page_config(
   page_title="AI Resume Analyzer",
#    page_icon
)

st.title('Resume Analyser')

st.sidebar.header('Profile')
selected_option = st.sidebar.selectbox('Select User Type', ('Admin', 'User'))

# create directory for temp pdf file
temp_pdf_folder = "temp_pdf_files"
os.makedirs(temp_pdf_folder, exist_ok=True)

# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    #close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# Upload a PDF file
uploaded_file = st.file_uploader("Upload a PDF File", type=["pdf"])

if uploaded_file is not None:
    # Save the uploaded file as a temporary file
    with st.spinner("Extracting PDF content..."):
        temp_pdf_path = os.path.join(temp_pdf_folder, f"temp_pdf_{random.randint(1, 100000)}.pdf")
    with open(temp_pdf_path, "wb") as temp_pdf_file:
        temp_pdf_file.write(uploaded_file.read())
            

    # Display the uploaded PDF
    show_pdf(temp_pdf_path)

    # loader
    with st.spinner("Loading data..."):
        time.sleep(10)

    # Extract text from the PDF and display it
    st.header("Extracted Text from PDF")
    pdf_text = pdf_reader(temp_pdf_path)
    st.write(pdf_text)

    # Generate a CSV download link for the extracted text
    csv_download_link = get_csv_download_link(pd.DataFrame({'Text': [pdf_text]}), "extracted_text.csv", "Download Extracted Text as CSV")
    st.markdown(csv_download_link, unsafe_allow_html=True)




   