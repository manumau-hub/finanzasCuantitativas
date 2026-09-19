import pandas as pd

# Create a dictionary with the income statement data
data = {
    'Item': ['Client A Services', 'Client B Services', 'R&D Grant', 'Direct Costs',
             'Salaries and Wages', 'Marketing and Advertising', 'Rent and Utilities',
             'Research and Development', 'General and Administrative', 'Interest Income',
             'Interest Expense', 'Income Tax Expense'],
    'Amount': [200000, 150000, 50000, -120000, -100000, -30000, -20000, -25000, -40000,
                1000, -2000, -15000]
}

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Calculate the Total row
total_row = df.groupby('Item', as_index=False)['Amount'].sum()
total_row.loc[len(total_row)] = ['Total Revenue', total_row['Amount'][:3].sum()]
total_row.loc[len(total_row)] = ['Gross Profit', total_row['Amount'][3] + total_row['Amount'][4]]

# Append the Total row to the DataFrame
df = df.append(total_row, ignore_index=True)

# Create a new Excel writer object
writer = pd.ExcelWriter('income_statement.xlsx', engine='xlsxwriter')

# Convert the DataFrame to an Excel object
df.to_excel(writer, sheet_name='Income Statement', index=False)

# Get the xlsxwriter workbook and worksheet objects
workbook = writer.book
worksheet = writer.sheets['Income Statement']

# Add a total format
total_format = workbook.add_format({'bold': True})

# Apply the total format to the Total rows
worksheet.set_row(len(df)-2, cell_format=total_format)
worksheet.set_row(len(df)-1, cell_format=total_format)

# Close the Pandas Excel writer and output the Excel file
writer.save()

print("Excel file 'income_statement.xlsx' has been created.")
