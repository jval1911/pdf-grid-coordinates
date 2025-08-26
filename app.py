import streamlit as st
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import red, blue, gray
import io
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="PDF Grid Coordinate Tool",
    page_icon="📐",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2em;
        font-weight: bold;
        color: #005670;
        margin-bottom: 0.5em;
    }
    .stButton>button {
        background-color: #3F4443;
        color: #CDD325;
        border: none;
        padding: 0.5em 1em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2D3231;
        color: #CDD325;
    }
</style>
""", unsafe_allow_html=True)

def create_grid_overlay(pdf_bytes):
    """
    Creates a PDF with grid overlay showing coordinates.
    Fixed settings: 50pt grid spacing, 7pt font
    """
    
    # Read the existing PDF
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    pdf_writer = PyPDF2.PdfWriter()
    
    # Fixed settings
    grid_spacing = 100
    coordinate_size = 7
    
    # Process each page
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        
        # Get page dimensions
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        # Create overlay
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))
        
        # Set grid line style
        can.setStrokeColor(gray)
        can.setLineWidth(0.3)
        
        # Draw vertical grid lines (X coordinates)
        x = 0
        while x <= page_width:
            can.line(x, 0, x, page_height)
            
            # Add x-coordinate labels
            can.setFillColor(blue)
            can.setFont("Helvetica", coordinate_size)
            can.drawString(x + 2, page_height - 10, str(int(x)))
            can.drawString(x + 2, 10, str(int(x)))
            
            x += grid_spacing
        
        # Draw horizontal grid lines (Y coordinates)
        y = 0
        while y <= page_height:
            can.line(0, y, page_width, y)
            
            # Add y-coordinate labels
            can.setFillColor(red)
            can.setFont("Helvetica", coordinate_size)
            can.drawString(10, y + 2, str(int(y)))
            can.drawString(page_width - 30, y + 2, str(int(y)))
            
            y += grid_spacing
        
        # Add page info header
        can.setFont("Helvetica-Bold", 10)
        can.setFillColor(red)
        info_text = f"Page {page_num + 1} - Dimensions: {int(page_width)} x {int(page_height)}"
        can.drawString(10, page_height - 25, info_text)
        
        can.save()
        packet.seek(0)
        
        # Merge overlay with page
        overlay_pdf = PyPDF2.PdfReader(packet)
        page.merge_page(overlay_pdf.pages[0])
        pdf_writer.add_page(page)
    
    # Write to bytes
    output_bytes = io.BytesIO()
    pdf_writer.write(output_bytes)
    output_bytes.seek(0)
    
    return output_bytes.getvalue()

# Main UI
st.markdown('<p class="main-header">PDF Grid Coordinate Tool</p>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    # Process immediately on upload
    pdf_bytes = uploaded_file.read()
    
    with st.spinner("Adding grid..."):
        try:
            # Process the PDF
            output_pdf = create_grid_overlay(pdf_bytes)
            
            # Download button
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"grid_{uploaded_file.name[:-4]}_{timestamp}.pdf"
            
            st.download_button(
                label="Download PDF with Grid",
                data=output_pdf,
                file_name=filename,
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
