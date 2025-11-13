import os
import math
import pandas as pd
from sqlalchemy import text
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, PageBreak
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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

def chunk_rows(rows, max_rows):
    """Yield chunks of rows with length <= max_rows (preserving header row at index 0)."""
    if not rows:
        return
    header = rows[0]
    body = rows[1:]
    for i in range(0, len(body), max_rows):
        chunk = [header] + body[i:i + max_rows]
        yield chunk

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
        pdf_filename = os.path.join(REPORT_PATH, f"Nodal_Analytics_Report_{timestamp}.pdf")
        logging.info(f"Generating PDF report at: {pdf_filename}")

        # Document and styles
        PAGE_SIZE = landscape(A3)
        left_margin = right_margin = top_margin = bottom_margin = 36  # points
        doc = SimpleDocTemplate(pdf_filename, pagesize=PAGE_SIZE,
                                leftMargin=left_margin, rightMargin=right_margin,
                                topMargin=top_margin, bottomMargin=bottom_margin)

        styles = getSampleStyleSheet()
        # Title style
        styles.add(ParagraphStyle(name='CandaraTitle', fontName='Candara', fontSize=18, leading=22, alignment=TA_CENTER))
        # Normal paragraph style for table cells (left aligned, wraps)
        styles.add(ParagraphStyle(name='CandaraNormalLeft', fontName='Candara', fontSize=10, leading=12, alignment=TA_LEFT))
        # Small bold style for headers inside cells
        styles.add(ParagraphStyle(name='CandaraHeader', fontName='Candara', fontSize=11, leading=13, alignment=TA_LEFT))

        elements = []

        # Title block
        elements.append(Paragraph("Nodal Officer Pending Summary Report", styles["CandaraTitle"]))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"Report Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles["CandaraNormalLeft"]))
        elements.append(Spacer(1, 12))

        # Compute usable page width and sensible column widths
        page_width, page_height = PAGE_SIZE
        usable_width = page_width - left_margin - right_margin
        # Two columns: Category (70%) and Pending Grievances (30%) - adjust if needed
        col_widths = [usable_width * 0.72, usable_width * 0.28]

        # Group data by officer
        grouped = df.groupby(["User", "Total Pending (All Categories)"], dropna=False)

        # We'll try to keep each officer header + first few rows together
        # but allow splitting if very large. Set a max rows per chunk to avoid very tall tables.
        # Estimate rows that comfortably fit on a page: conservatively 35 rows for A3 landscape
        max_rows_per_chunk = 40

        for (user, total), group in grouped:
            officer_name = user if pd.notna(user) else "Unknown Officer"
            total_pending = int(total) if pd.notna(total) else 0

            # Officer header line (kept with following table)
            officer_header = Paragraph(
                f"<b>Officer:</b> {officer_name} &nbsp;&nbsp;&nbsp;&nbsp; <b>Total Pending:</b> {total_pending}",
                styles["CandaraHeader"]
            )

            # Build table data (header + rows)
            sub_df = group[["Category", "Pending Grievances"]].fillna("")
            table_data = [
                [Paragraph("<b>Category</b>", styles["CandaraHeader"]),
                 Paragraph("<b>Pending Grievances</b>", styles["CandaraHeader"])]
            ]

            for _, row in sub_df.iterrows():
                category = str(row.get("Category", ""))
                pending = str(row.get("Pending Grievances", ""))
                table_data.append([
                    Paragraph(category, styles["CandaraNormalLeft"]),
                    Paragraph(pending, styles["CandaraNormalLeft"])
                ])

            # If the table is short, add it as one block and keep it with header
            if len(table_data) <= max_rows_per_chunk:
                tbl = Table(table_data, colWidths=col_widths, repeatRows=1, hAlign='LEFT')
                tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#00665F")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, -1), 'Candara'),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                ]))
                elements.append(KeepTogether([officer_header, Spacer(1, 6), tbl, Spacer(1, 12)]))
            else:
                # Large table: break into multiple chunks that each have header row
                # chunk_rows yields segments with header included
                for i, chunk in enumerate(chunk_rows(table_data, max_rows_per_chunk - 1)):  # -1 because chunk_rows adds header
                    tbl = Table(chunk, colWidths=col_widths, repeatRows=1, hAlign='LEFT')
                    tbl.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#00665F")),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('FONTNAME', (0, 0), (-1, -1), 'Candara'),
                        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ]))

                    # For the first chunk keep it with the officer header
                    if i == 0:
                        elements.append(KeepTogether([officer_header, Spacer(1, 6), tbl, Spacer(1, 12)]))
                    else:
                        elements.append(tbl)
                        elements.append(Spacer(1, 12))

        # Build PDF
        doc.build(elements)
        logging.info(f"✅ PDF generated successfully: {pdf_filename}")
        print(f"✅ PDF generated successfully: {pdf_filename}")

    except Exception as e:
        logging.error(f"❌ Error during PDF generation: {str(e)}", exc_info=True)
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    generate_pdf2_from_sql()

