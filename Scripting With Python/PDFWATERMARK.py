from PyPDF2 import PdfReader, PdfWriter

# Input files
input_pdf = "superpdf.pdf"        # The main PDF
watermark_pdf = "water.pdf"       # The watermark PDF (should contain 1 page)

# Output file
output_pdf = "watermarked_output.pdf"

# Create reader and writer objects
reader = PdfReader(input_pdf)
writer = PdfWriter()

# Load the watermark page
watermark = PdfReader(watermark_pdf).pages[0]

# Apply watermark to each page
for page in reader.pages:
    page.merge_page(watermark)   # Overlay watermark on the page
    writer.add_page(page)

# Save the result
with open(output_pdf, "wb") as output_file:
    writer.write(output_file)

print(f"✅ Watermark added successfully! Saved as {output_pdf}")
