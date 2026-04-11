"""
QualityPulse — Export Utilities
Helper functions to export pandas DataFrames to various formats like Excel with professional styling.
"""

import pandas as pd
import io
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

def format_excel_sheet(worksheet, auto_filter=True):
    """Applies professional styling to a given openpyxl worksheet."""
    # Define styles
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='1A1A2E', end_color='1A1A2E', fill_type='solid')
    header_alignment = Alignment(horizontal='center', vertical='center')
    
    border_side = Side(style='thin', color='CBD5E1')
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    
    alt_fill = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')
    white_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
    
    # 1. Format header row
    if worksheet.max_row > 0:
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
            
        worksheet.freeze_panes = 'A2'
        
        # Auto-filter
        if auto_filter:
            worksheet.auto_filter.ref = worksheet.dimensions

    # 2. Format data rows and adjust column widths
    for col_idx, col in enumerate(worksheet.columns, 1):
        max_length = 0
        column_letter = get_column_letter(col_idx)
        
        for row_idx, cell in enumerate(col, 1):
            # Apply styling only to data cells, not header
            if row_idx > 1:
                # Alternate fill color and apply border
                cell.fill = alt_fill if row_idx % 2 == 0 else white_fill
                cell.border = thin_border
                
            # Calculate max width for auto-sizing
            try:
                cell_value = str(cell.value) if cell.value is not None else ""
                lines = cell_value.split('\n')
                longest_line = max(len(line) for line in lines) if lines else 0
                if longest_line > max_length:
                    max_length = longest_line
            except:
                pass
                
        # Set max column width (cap at 60 to prevent absurdly wide columns)
        adjusted_width = min(max_length + 3, 60)
        worksheet.column_dimensions[column_letter].width = adjusted_width

def to_excel(df: pd.DataFrame) -> bytes:
    """
    Converts a pandas DataFrame to an Excel file format in memory,
    with professional table styling applied.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Veriler')
        worksheet = writer.sheets['Veriler']
        format_excel_sheet(worksheet)
    
    return output.getvalue()
