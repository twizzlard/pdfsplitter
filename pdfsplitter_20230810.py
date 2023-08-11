import PyPDF2
import zipfile
import io
import streamlit as st

def split_pdf(uploaded_file, locations_txt_file=None):
    zip_buffer = io.BytesIO()

    locations = [
        '60500 GENERAL ADMINI', '60506 ECOPARK', '60523-IAH AMBASS HOU', '60524-HOB AMBASS',
        '64065A IAH VALET HOU', '64066B IAH VALET HOU', '64067C IAH VALET HOU', '64077 HOB VALET',
        '64197 ECOPARK', 'IAH AMBASS FAC MGR H', 'IAH VALET FAC MGR HO'
    ]

    # If a txt file is uploaded, update the locations from the contents of the file
    if locations_txt_file is not None:
        locations = locations_txt_file.read().decode('utf-8').split('\n')

    if 'GRAND TOTALS' not in locations:
        locations.append('GRAND TOTALS')

    st.write("Locations:", locations)
    
    reader = PyPDF2.PdfReader(uploaded_file)
    num_pages = len(reader.pages)
    start_page = 0

        # Create a ZIP file in memory
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
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
                pdf_bytes = io.BytesIO()
                writer = PyPDF2.PdfWriter()
                for split_page_num in range(start_page, end_page + 1):
                    writer.add_page(reader.pages[split_page_num])
                writer.write(pdf_bytes)
                pdf_bytes.seek(0)
                output_filename = f'{str(start_page + 1).zfill(2)}-{str(end_page + 1).zfill(2)}_{location}_{uploaded_file.name[:-4]}.pdf'
                zip_file.writestr(output_filename, pdf_bytes.read())
                
                st.text(f"Created: {output_filename}")
                start_page = end_page + 1
            else:
                st.text(f"Could not find the next location {next_location}")

        # Handle the last location until the end of the PDF
        pdf_bytes = io.BytesIO()
        writer = PyPDF2.PdfWriter()
        for split_page_num in range(start_page, num_pages):
            writer.add_page(reader.pages[split_page_num])
            
        output_filename = f'{str(start_page + 1).zfill(2)}-{num_pages}_{locations[-1]}_{uploaded_file.name[:-4]}.pdf'
        writer.write(pdf_bytes)
        pdf_bytes.seek(0)
        zip_file.writestr(output_filename, pdf_bytes.read())

        st.text(f"Created: {output_filename}")

    st.success('Successfully split the PDF.')
    return zip_buffer.getvalue()

# Streamlit App
st.title("PDF Splitter")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
locations_txt_file = st.file_uploader("Optionally, upload a txt file for locations", type="txt")

if uploaded_file is not None:
    st.text("Processing the PDF. This may take a moment...")
    zip_bytes = split_pdf(uploaded_file, locations_txt_file)
    st.download_button("Download ZIP File", zip_bytes, "split_pdfs.zip", "application/zip")
