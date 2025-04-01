RUN=poetry run
WGET=wget

local/goldData.xlsx:
	curl -o $@ "https://gold.jgi.doe.gov/download?mode=site_excel"

local/goldData_biosamples.csv: local/goldData.xlsx # for counting biosamples with a path that corresponds to en env_local_scale from local/goldterms-env_local_scale-of-environmental-terrestrial-soil-counts.txt
	$(RUN) python -c "import pandas as pd; import sys; df = pd.read_excel(sys.argv[1], sheet_name=sys.argv[3]); df['BIOSAMPLE ECOSYSTEM PATH ID'] = df['BIOSAMPLE ECOSYSTEM PATH ID'].fillna(0).astype(int); df.to_csv(sys.argv[2], index=False)" $< $@ Biosample
