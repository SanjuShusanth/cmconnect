import os
import pandas as pd
from sqlalchemy import text
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, landscape, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import logging
from config_cloud import *

# ======================================================
# Logging Configuration
# ======================================================
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "report_generation.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def generate_pdf_from_sql():
    try:
        logging.info("===== PDF Report Generation Started =====")

        # Step 1: Read SQL Query
        logging.info(f"Reading SQL query from: {SQL_QUERY_PATH1}")
        if not os.path.exists(SQL_QUERY_PATH1):
            raise FileNotFoundError(f"SQL file not found at path: {SQL_QUERY_PATH1}")

        with open(SQL_QUERY_PATH1, 'r') as file:
            sql_query = file.read().strip()

        if not sql_query:
            raise ValueError("SQL file is empty. Please add a valid query.")

        # Step 2: Execute Query
        logging.info("Connecting to database and executing SQL query...")
        with engine.connect() as connection:
            df = pd.read_sql(text(sql_query), connection)

        logging.info(f"SQL query executed successfully. Rows fetched: {len(df)}")

        if df.empty:
            logging.warning("Query returned no data. PDF generation skipped.")
            print("⚠️ Query returned no data. Please check the SQL query or database.")
            return

        # Step 3: Register Candara Font
        candara_font_path = FONT_PATH
        if not os.path.exists(candara_font_path):
            raise FileNotFoundError(f"Candara font not found at: {candara_font_path}")

        pdfmetrics.registerFont(TTFont("Candara", candara_font_path))

        # Step 4: Prepare PDF Output Path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = os.path.join(REPORT_PATH, f"Nodal_Officer_Report_{timestamp}.pdf")
        logging.info(f"Generating PDF report at: {pdf_filename}")

        doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(A3))
        styles = getSampleStyleSheet()

        # Override default styles with Candara
        styles.add(ParagraphStyle(name='CandaraTitle', fontName='Candara', fontSize=18, leading=22, alignment=1))
        styles.add(ParagraphStyle(name='CandaraNormal', fontName='Candara', fontSize=11, leading=14))

        elements = []

        # Step 5: Title Section
        elements.append(Paragraph("Nodal Officer Grievance Summary Report", styles["CandaraTitle"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Report Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles["CandaraNormal"]))
        elements.append(Spacer(1, 12))

        # Step 6: Data Table (Auto column widths + Word wrapping + Centered)

        # Define a wrapping style for cells
        wrap_style = ParagraphStyle(
            name='WrapStyle',
            fontName='Candara',
            fontSize=10,
            alignment=TA_CENTER,
            leading=12
        )

        # Convert DataFrame to table data with wrapped text
        table_data = []
        headers = [Paragraph(f"<b>{col}</b>", wrap_style) for col in df.columns]
        table_data.append(headers)

        # Wrap each cell text
        for _, row in df.iterrows():
            wrapped_row = [Paragraph(str(cell), wrap_style) for cell in row]
            table_data.append(wrapped_row)

        # Calculate proportional column widths based on text length
        page_width, _ = landscape(A3)
        usable_width = page_width * 0.8

        col_lengths = []
        for col in df.columns:
            sample_texts = df[col].astype(str).head(30)
            avg_len = sample_texts.map(len).mean() + len(col)
            col_lengths.append(avg_len)

        total_len = sum(col_lengths)
        col_widths = [(usable_width * (length / total_len)) for length in col_lengths]

        # Create and style table
        table = Table(table_data, colWidths=col_widths, repeatRows=1, hAlign='CENTER')

        table.setStyle(TableStyle([
            # Base font for all
            ('FONTNAME', (0, 0), (-1, -1), 'Candara'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),

            # Header row (apply color last to ensure it sticks)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#FFE699")),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            # Grid and alternating rows
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),

            # Spacing
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))




        elements.append(Spacer(1, 12))
        elements.append(table)
        elements.append(Spacer(1, 12))


        # Step 7: Build PDF
        doc.build(elements)
        logging.info(f"✅ PDF generated successfully: {pdf_filename}")
        print(f"✅ PDF generated successfully: {pdf_filename}")

    except Exception as e:
        logging.error(f"❌ Error during PDF generation: {str(e)}", exc_info=True)
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_pdf_from_sql()
