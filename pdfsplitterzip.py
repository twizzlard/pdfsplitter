import streamlit as st
import PyPDF2
import zipfile
import os
import tempfile

locations = [
    '60500 GENERAL ADMINI', '60506 ECOPARK', '60523-IAH AMBASS HOU', '60524-HOB AMBASS',
    '64065A IAH VALET HOU', '64066B IAH VALET HOU', '64067C IAH VALET HOU', '64077 HOB VALET',
    '64197 ECOPARK', 'IAH AMBASS FAC MGR H', 'IAH VALET FAC MGR HO', 'GRAND TOTALS'
]

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.write("File uploaded successfully!")

    # Create a temporary directory to store split PDF files
    temp_dir = tempfile.mkdtemp()

    reader = PyPDF2.PdfReader(uploaded_file)
    num_pages = len(reader.pages)
    start_page = 0

    for i, location in enumerate(locations[:-1]):
        next_location = locations[i + 1]
        end_page = None

        # Loop through the pages and find the page where the next location appears
        for page_num in range(start_page, num_pages):
            page_content = reader.pages[page_num].extract_text()
            if next_location in page_content:
                end_page = page_num - 1
                break

        if end_page is not None:
            writer = PyPDF2.PdfWriter()
            for split_page_num in range(start_page, end_page + 1):
                writer.add_page(reader.pages[split_page_num])

            output_filename = f'{str(start_page + 1).zfill(2)}-{str(end_page + 1).zfill(2)}_{location}.pdf'
            output_path = os.path.join(temp_dir, output_filename)

            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            st.write(f"Created file: {output_filename}")

            start_page = end_page + 1
        else:
            st.write(f"Could not find the next location {next_location}")

    # Handle the last location until the end of the PDF
    writer = PyPDF2.PdfWriter()
    for split_page_num in range(start_page, num_pages):
        writer.add_page(reader.pages[split_page_num])

    output_filename = f'{str(start_page + 1).zfill(2)}-{num_pages}_{locations[-1]}.pdf'
    output_path = os.path.join(temp_dir, output_filename)
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
        
    st.write(f"Created file: {output_filename}")

    # Zip the split PDF files and provide a download link
    zip_path = os.path.join(temp_dir, 'split_pdfs.zip')
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for filename in os.listdir(temp_dir):
            if filename.endswith('.pdf'):
                zip_file.write(os.path.join(temp_dir, filename), filename)

    st.write("Successfully split the PDF.")
    st.download_button("Download the ZIP file", zip_path)
