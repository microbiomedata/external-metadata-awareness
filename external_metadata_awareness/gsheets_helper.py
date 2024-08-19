from pathlib import Path
import gsheet_pandas
import pandas as pd

# Define the path to your credentials
secret_path = Path('/Users/MAM/.config/gspread').resolve()

# Setup gsheet_pandas with the directory containing your credentials.json
gsheet_pandas.setup(credentials_dir=secret_path / 'credentials.json', token_dir=secret_path / 'token.json')

df = pd.from_gsheet('1YCNAK3ggCwO0cyo7kSV6dFTy9oHc_mxWOwNxBv3Fpco',
                    sheet_name='Sheet1')

print(df)
