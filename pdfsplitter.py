import streamlit as st
import PyPDF2
import re
import zipfile
import shutil
import os


def split_pdf(file_bytes):
    reader = PyPDF2.PdfReader(file_bytes)
    num_pages = len(reader.pages)
    content = ""

    # Read all pages into one content variable
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        content += page.extract_text()

    # Use regex to find all occurrences of the pattern with page numbers
    pattern = re.compile(
        r'Contribution Total:.*?(?:REGULAR PAY.*?Break Total:|Break Total:.*?REGULAR PAY).*?(?:Contribution|Deduction) Total:.*?(?:Contribution|Deduction) Total:.*?Page (\d+)',
        flags=re.DOTALL)
    matches = pattern.findall(content)

    # Directory to save the individual PDFs
    output_dir = 'output_pdfs'
    os.makedirs(output_dir, exist_ok=True)

    # Start splitting the PDF
    start_page = 0
    for page_num in matches:
        end_page = int(page_num) - 1  # Convert page number to 0-based index
        writer = PyPDF2.PdfWriter()
        for split_page_num in range(start_page, end_page + 1):
            writer.add_page(reader.pages[split_page_num])
        with open(f'{output_dir}/split_{start_page + 1}_{end_page + 1}.pdf', 'wb') as output_file:
            writer.write(output_file)
        start_page = end_page + 1

    # If there are pages left after the last split
    if start_page < num_pages:
        writer = PyPDF2.PdfWriter()
        for split_page_num in range(start_page, num_pages):
            writer.add_page(reader.pages[split_page_num])
        with open(f'{output_dir}/split_{start_page + 1}_{num_pages}.pdf', 'wb') as output_file:
            writer.write(output_file)

    # Zip the files
    shutil.make_archive('split_pdfs', 'zip', '.', 'output_pdfs')

    # Clean up the individual PDFs
    shutil.rmtree(output_dir)

    print(f'Successfully split the PDF.')


# Streamlit App
st.title("PDF Splitter")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    split_pdf(uploaded_file)
    st.success('PDF split successfully!')

    # Provide download link for ZIP
    st.markdown('Download the split PDFs [here](split_pdfs.zip)')
