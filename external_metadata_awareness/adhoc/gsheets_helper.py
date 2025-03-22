from pathlib import Path
import gsheet_pandas
import pandas as pd

# Define the path to your credentials
secret_path = Path('/Users/MAM/.config/gspread').resolve()

# Setup gsheet_pandas with the directory containing your credentials.json
gsheet_pandas.setup(credentials_dir=secret_path / 'credentials.json', token_dir=secret_path / 'token.json')

# Soil-value-sets
sheet_id = '1UUA-WfZG2-UMtIuX5TPsE7hCfPFaOCHhjUYwZPjiAjQ'
# input_file = "../local/EnvBroadScaleSoilEnum-pvs-keys-parsed-unique.csv"
# target_sheet = 'EnvBroadScaleSoilEnum'
input_file = "../local/soil-env_broad_scale-algebraic.csv"
target_sheet = 'soil-env_broad_scale-algebraic'


# just do this once? or cache it?
def num_to_col_letters(num):
    letters = ''
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def df_shape_to_sheet_range(shape):
    rows, cols = shape
    start_col = 'A'
    end_col = num_to_col_letters(cols)  # Convert column count to column letter
    start_row = '1'
    end_row = str(rows + 1)  # for header row aka drop_columns=False
    return f'!{start_col}{start_row}:{end_col}{end_row}'


df = pd.read_csv(input_file)
df = df[['normalized_curie', 'normalized_label']]

range_string = df_shape_to_sheet_range(df.shape)

# print(range_string)

# df = pd.from_gsheet(sheet_id,
#                     sheet_name='EnvBroadScaleSoilEnum',
#                     range_name=range_string)

# print(df)

df.to_gsheet(sheet_id,
             sheet_name=target_sheet,
             range_name=range_string,
             drop_columns=False, )  # Upload column names or not; Optional
