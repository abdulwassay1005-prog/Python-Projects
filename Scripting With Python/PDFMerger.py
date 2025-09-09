from PyPDF2 import PdfMerger

# Create a PdfMerger object
merger = PdfMerger()

# List of PDF files to merge (in order)
pdf_files = ["dummy1.pdf", "twopager.pdf", "water.pdf"]

# Loop through all files and append them
for pdf in pdf_files:
    merger.append(pdf)

# Write the merged PDF to a new file
merger.write("superpdf.pdf")
merger.close()

print("PDFs merged successfully into 'superpdf.pdf'")
