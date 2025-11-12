from fpdf import FPDF
import os
from config import output_file_path, FONT_PATH

WIDTH = 210
HEIGHT = 297

pdf = FPDF()
pdf.add_page()

# ✅ Add Candara font
candara_font_path = FONT_PATH 
pdf.add_font('Candara', '', candara_font_path, uni=True)

# --- Title Section ---
pdf.set_font('Candara', '', 18)
pdf.ln(10)  # add top space
title = "Chief Minister Connect Program (CM Connect)"
pdf.cell(0, 10, title, ln=True, align='C')  # center align title
pdf.ln(10)  # space below title

# --- Content Section ---
pdf.set_font('Candara', '', 8)

content = """An initiative aimed to enhance citizen-centric governance, promoting transparency,
and ensuring timely resolution of grievances of the citizens. The project was launched by 
Hon’ble Chief Minister on 15th Feb 2024. Citizens can raise their grievances through Helpline 1971 and Toll-Free No. 1800-3456-851.
"""

# --- Center align the paragraph manually ---
for line in content.split('\n'):
    line = line.strip()
    if line == "":
        pdf.ln(6)
        continue
    text_width = pdf.get_string_width(line)
    page_width = pdf.w - 2 * pdf.l_margin
    pdf.set_x((pdf.w - text_width) / 2)
    pdf.cell(text_width, 8, line, ln=True)

# --- Save PDF ---
pdf_filename = os.path.join(output_file_path, "TestReport.pdf")
pdf.output(pdf_filename)

print(f"✅ PDF generated successfully: {pdf_filename}")
