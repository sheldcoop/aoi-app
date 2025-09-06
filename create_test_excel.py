import pandas as pd

# Create a sample dataframe
data = {
    'DEFECT_TYPE': ['Nick', 'Short', 'Missing Feature', 'Cut'],
    'UNIT_INDEX_X': [1, 2, 3, 4],
    'UNIT_INDEX_Y': [5, 6, 7, 8],
    'EXTRA_COLUMN': ['A', 'B', 'C', 'D']
}
df = pd.DataFrame(data)

# Create a test excel file
writer = pd.ExcelWriter('tests/test_data.xlsx', engine='xlsxwriter')
df.to_excel(writer, index=False)
writer.close()

# Create a test excel file with missing columns
data_missing = {
    'DEFECT_TYPE': ['Nick', 'Short'],
    'UNIT_INDEX_X': [1, 2],
}
df_missing = pd.DataFrame(data_missing)
writer_missing = pd.ExcelWriter('tests/test_data_missing_cols.xlsx', engine='xlsxwriter')
df_missing.to_excel(writer_missing, index=False)
writer_missing.close()
