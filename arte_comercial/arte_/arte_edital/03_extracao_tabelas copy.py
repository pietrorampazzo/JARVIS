import os
import re

import pandas as pd
import pdfplumber

try:
    import camelot
except ImportError:
    camelot = None

def clean_cell(cell):
    if cell is None or str(cell).strip() == '':
        return ""
    return re.sub(r"\s+", " ", str(cell)).strip()

def is_item_start(cell):
    if not cell:
        return False
    cell = str(cell).strip()
    # Starts with number
    if re.match(r"^\d+\b", cell):
        return True
    # "ITEM 10"
    if re.match(r"^ITEM\s*\d+", cell, re.IGNORECASE):
        return True
    return False

def extract_tables_with_pdfplumber(pdf_path):
    print(f"\nProcessando com pdfplumber: {os.path.basename(pdf_path)}")

    all_rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        cleaned_row = [clean_cell(cell) for cell in row]
                        if any(cleaned_row):  # Skip empty rows
                            all_rows.append(cleaned_row)

    print(f"Total de linhas extraidas: {len(all_rows)}")
    return all_rows

def extract_tables_with_camelot(pdf_path):
    if camelot is None:
        raise ImportError("camelot-py nao esta instalado neste ambiente.")

    tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    all_rows = []

    for table in tables:
        df = table.df
        for _, row in df.iterrows():
            cleaned_row = [clean_cell(cell) for cell in row]
            if any(cleaned_row):
                all_rows.append(cleaned_row)

    return all_rows

def group_items(rows):
    items = []
    current_item = None

    for row in rows:
        first_cell = row[0] if row else ""

        if is_item_start(first_cell):
            if current_item:
                items.append(current_item)
            current_item = row.copy()
        else:
            if current_item:
                # Merge with previous row if continuation
                current_item = [a + " " + b if a and b else a or b for a, b in zip(current_item, row)]

    if current_item:
        items.append(current_item)

    return items

def export_items(items, output_path):
    if not items:
        print("Nenhum item identificado. Arquivo nao gerado.")
        return

    max_cols = max(len(i) for i in items)
    normalized = []

    for item in items:
        row = item + [""] * (max_cols - len(item))
        normalized.append(row)

    df = pd.DataFrame(normalized)
    df.to_excel(output_path, index=False, header=False)
    print(f"Arquivo salvo em: {output_path}")

def process_pdf(pdf_path):
    if camelot is not None:
        rows = extract_tables_with_camelot(pdf_path)
    else:
        rows = extract_tables_with_pdfplumber(pdf_path)
    items = group_items(rows)

    output_dir = os.path.dirname(pdf_path)
    pdf_folder_name = os.path.basename(output_dir)
    output_filename = f"{pdf_folder_name}_referencia.xlsx"
    output_path = os.path.join(output_dir, output_filename)

    export_items(items, output_path)

    print("\nExemplo de linhas:")
    for i in items[:3]:
        print(str(i).encode("ascii", "backslashreplace").decode("ascii"))

if __name__ == "__main__":
    pdf_path = r"C:\Users\pietr\OneDrive\.vscode\arte_\DOWNLOADS\EDITAIS\CREA\termo_referencia.pdf"
    process_pdf(pdf_path)
