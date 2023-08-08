import streamlit as st
import PyPDF2
import re
from io import BytesIO


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

    # Start splitting the PDF
    start_page = 0
    for page_num in matches:
        end_page = int(page_num) - 1  # Convert page number to 0-based index
        writer = PyPDF2.PdfWriter()
        for split_page_num in range(start_page, end_page + 1):
            writer.add_page(reader.pages[split_page_num])

        # Create a download link
        buffer = BytesIO()
        writer.write(buffer)
        buffer.seek(0)

        st.download_button(
            label=f'Download split_{start_page + 1}_{end_page + 1}.pdf',
            data=buffer,
            file_name=f'split_{start_page + 1}_{end_page + 1}.pdf',
            mime='application/pdf'
        )
        start_page = end_page + 1

    # If there are pages left after the last split
    if start_page < num_pages:
        writer = PyPDF2.PdfWriter()
        for split_page_num in range(start_page, num_pages):
            writer.add_page(reader.pages[split_page_num])

        buffer = BytesIO()
        writer.write(buffer)
        buffer.seek(0)

        st.download_button(
            label=f'Download split_{start_page + 1}_{num_pages}.pdf',
            data=buffer,
            file_name=f'split_{start_page + 1}_{num_pages}.pdf',
            mime='application/pdf'
        )

    st.success('PDF split successfully!')


# Streamlit App
st.title("PDF Splitter")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.text("Processing the PDF. This may take a moment...")  # Inform the user that processing is underway
    split_pdf(uploaded_file)
    st.text("Processing complete!")  # Optionally, inform the user when processing is done
