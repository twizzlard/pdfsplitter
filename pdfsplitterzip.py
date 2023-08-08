import streamlit as st
import PyPDF2
import re
import zipfile
import io

def split_pdf(file_bytes):
    reader = PyPDF2.PdfReader(file_bytes)
    num_pages = len(reader.pages)
    content = ""
    zip_buffer = io.BytesIO()

    # Read all pages into one content variable
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        content += page.extract_text()

    # Use regex to find all occurrences of the pattern with page numbers
    pattern = re.compile(
        r'Contribution Total:.*?(?:REGULAR PAY.*?Break Total:|Break Total:.*?REGULAR PAY).*?(?:Contribution|Deduction) Total:.*?(?:Contribution|Deduction) Total:.*?Page (\d+)',
        flags=re.DOTALL)
    matches = pattern.findall(content)

    # Create a ZIP file in memory
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        # Start splitting the PDF
        start_page = 0
        for page_num in matches:
            end_page = int(page_num) - 1  # Convert page number to 0-based index
            pdf_bytes = io.BytesIO()
            writer = PyPDF2.PdfWriter()
            for split_page_num in range(start_page, end_page + 1):
                writer.add_page(reader.pages[split_page_num])
            writer.write(pdf_bytes)
            pdf_bytes.seek(0)
            zip_file.writestr(f'split_{start_page + 1}_{end_page + 1}.pdf', pdf_bytes.read())
            start_page = end_page + 1

        # If there are pages left after the last split
        if start_page < num_pages:
            pdf_bytes = io.BytesIO()
            writer = PyPDF2.PdfWriter()
            for split_page_num in range(start_page, num_pages):
                writer.add_page(reader.pages[split_page_num])
            writer.write(pdf_bytes)
            pdf_bytes.seek(0)
            zip_file.writestr(f'split_{start_page + 1}_{num_pages}.pdf', pdf_bytes.read())

    print(f'Successfully split the PDF.')
    return zip_buffer.getvalue()

# Streamlit App
st.title("PDF Splitter")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.text("Processing the PDF. This may take a moment...")
    zip_bytes = split_pdf(uploaded_file)
    st.success('PDF split successfully!')
    st.download_button("Download ZIP File", zip_bytes, "split_pdfs.zip", "application/zip")
