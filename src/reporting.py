# src/reporting.py
# This module contains all functions related to generating professional, presentation-ready reports.

import pandas as pd
import io

def generate_excel_report(full_df, panel_rows, panel_cols):
    """
    Generates a comprehensive, multi-sheet Excel report with professional
    formatting and an embedded summary chart.
    
    Args:
        full_df (pd.DataFrame): The complete, unfiltered dataframe.
        panel_rows (int): The number of rows in a single panel.
        panel_cols (int): The number of columns in a single panel.

    Returns:
        bytes: The Excel file as an in-memory bytes object.
    """
    output_buffer = io.BytesIO()

    with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # --- Define Professional Formats ---
        header_format = workbook.add_format({
            'bold': True, 'text_wrap': True, 'valign': 'top', 
            'fg_color': '#D7E4BC', 'border': 1, 'align': 'center'
        })
        cell_format = workbook.add_format({'border': 1})
        percent_format = workbook.add_format({'num_format': '0.00%', 'border': 1})

        # --- Sheet 1: Quarterly Summary ---
        worksheet = workbook.add_worksheet('Quarterly Summary')
        writer.sheets['Quarterly Summary'] = worksheet

        kpi_data = []
        quadrants = ['Q1', 'Q2', 'Q3', 'Q4']
        
        for quad in quadrants:
            quad_df = full_df[full_df['QUADRANT'] == quad]
            kpi_data.append({"Quadrant": quad, "Total Defects": len(quad_df), "Defect Density": len(quad_df) / (panel_rows * panel_cols)})
        
        total_defects_all = len(full_df)
        density_all = total_defects_all / (4 * panel_rows * panel_cols) if (panel_rows * panel_cols) > 0 else 0
        kpi_data.append({"Quadrant": "Total", "Total Defects": total_defects_all, "Defect Density": density_all})
        
        summary_df = pd.DataFrame(kpi_data)
        
        summary_df.to_excel(writer, sheet_name='Quarterly Summary', startrow=1, header=False, index=False)
        
        for col_num, value in enumerate(summary_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        for row_num in range(len(summary_df)):
            worksheet.write(row_num + 1, 0, summary_df.iloc[row_num, 0], cell_format)
            worksheet.write(row_num + 1, 1, summary_df.iloc[row_num, 1], cell_format)
            worksheet.write(row_num + 1, 2, summary_df.iloc[row_num, 2], workbook.add_format({'num_format': '0.00', 'border': 1}))

        worksheet.autofit()
        
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name':       'Total Defects by Quadrant',
            'categories': ['Quarterly Summary', 2, 0, 5, 0],
            'values':     ['Quarterly Summary', 2, 1, 5, 1],
        })
        chart.set_title({'name': 'Defect Count Comparison'})
        chart.set_legend({'position': 'none'})
        worksheet.insert_chart('E2', chart)

        # --- Create a separate sheet for each quadrant's top offenders ---
        for quad in quadrants:
            quad_df = full_df[full_df['QUADRANT'] == quad]
            if not quad_df.empty:
                sheet_name = f'{quad} Top Defects'
                worksheet = workbook.add_worksheet(sheet_name)
                writer.sheets[sheet_name] = worksheet
                
                top_offenders = quad_df['DEFECT_TYPE'].value_counts().reset_index()
                top_offenders.columns = ['Defect Type', 'Count']
                top_offenders['Percentage'] = (top_offenders['Count'] / len(quad_df))
                
                top_offenders.to_excel(writer, sheet_name=sheet_name, startrow=1, header=False, index=False)
                
                for col_num, value in enumerate(top_offenders.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                worksheet.set_column('C:C', 12, percent_format)
                worksheet.autofit()

        # --- Final Sheet: Full Defect List (Cleaned) ---
        # --- BUG FIX: Select only the relevant columns for the final report ---
        report_columns = ['UNIT_INDEX_X', 'UNIT_INDEX_Y', 'DEFECT_TYPE', 'QUADRANT']
        # Ensure columns exist before trying to select them
        final_df = full_df[[col for col in report_columns if col in full_df.columns]]

        final_df.to_excel(writer, sheet_name='Full Defect List', startrow=1, header=False, index=False)
        worksheet = writer.sheets['Full Defect List']
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        worksheet.autofit()

    excel_bytes = output_buffer.getvalue()
    return excel_bytes

