import os
import pandas as pd
from sqlalchemy import text
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import logging
from config_cloud import *

# ======================================================
# Logging Configuration
# ======================================================
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "report_generation1.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def generate_pdf2_from_sql():
    try:
        logging.info("===== PDF Report Generation Started =====")

        # Step 1: Read SQL Query
        logging.info(f"Reading SQL query from: {SQL_QUERY_PATH2}")
        if not os.path.exists(SQL_QUERY_PATH2):
            raise FileNotFoundError(f"SQL file not found at path: {SQL_QUERY_PATH2}")

        with open(SQL_QUERY_PATH2, 'r') as file:
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
        styles.add(ParagraphStyle(name='CandaraTitle', fontName='Candara', fontSize=18, leading=22, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='CandaraNormal', fontName='Candara', fontSize=11, leading=14))

        elements = []

        # Step 5: Title Section
        elements.append(Paragraph("Nodal Officer Pending Summary Report", styles["CandaraTitle"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Report Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles["CandaraNormal"]))
        elements.append(Spacer(1, 18))

        # Step 6: Format data by officer (grouped layout)
        grouped = df.groupby(["User", "Total Pending (All Categories)"], dropna=False)

        for (user, total), group in grouped:
            officer_name = user if pd.notna(user) else "Unknown Officer"
            total_pending = int(total) if pd.notna(total) else 0

            # Officer Header
            officer_header = Paragraph(
                f"<b>Officer:</b> {officer_name} &nbsp;&nbsp;&nbsp;&nbsp; <b>Total Pending:</b> {total_pending}",
                styles["CandaraNormal"]
            )
            elements.append(officer_header)
            elements.append(Spacer(10, 6))

            # Create table for this officer
            sub_df = group[["Category", "Pending Grievances"]]
            table_data = [
                [Paragraph("<b>Category</b>", styles["CandaraNormal"]),
                 Paragraph("<b>Pending Grievances</b>", styles["CandaraNormal"])]
            ]

            for _, row in sub_df.iterrows():
                category = str(row.get("Category", ""))
                pending = str(row.get("Pending Grievances", ""))
                table_data.append([
                    Paragraph(category, styles["CandaraNormal"]),
                    Paragraph(pending, styles["CandaraNormal"])
                ])

            sub_table = Table(table_data, colWidths=[350, 120], hAlign='CENTER')
            sub_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#00665F")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, -1), 'Candara'),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))

            elements.append(sub_table)
            elements.append(Spacer(1, 18))

        # Step 7: Build PDF
        doc.build(elements)
        logging.info(f"✅ PDF generated successfully: {pdf_filename}")
        print(f"✅ PDF generated successfully: {pdf_filename}")

    except Exception as e:
        logging.error(f"❌ Error during PDF generation: {str(e)}", exc_info=True)
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    generate_pdf2_from_sql()
