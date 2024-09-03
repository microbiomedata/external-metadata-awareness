RUN=poetry run
WGET=wget

local/goldData.xlsx:
	curl -o $@ "https://gold.jgi.doe.gov/download?mode=site_excel"

local/goldData_biosamples.csv: local/goldData.xlsx # for counting biosamples with a path that corresponds to en env_local_scale from local/goldterms-env_local_scale-of-environmental-terrestrial-soil-counts.txt
	$(RUN) python -c "import pandas as pd; import sys; df = pd.read_excel(sys.argv[1], sheet_name=sys.argv[3]); df['BIOSAMPLE ECOSYSTEM PATH ID'] = df['BIOSAMPLE ECOSYSTEM PATH ID'].fillna(0).astype(int); df.to_csv(sys.argv[2], index=False)" $< $@ Biosample

local/goldterms-env_local_scale-of-environmental-terrestrial-soil.tsv: local/envo_goldterms.db # counts by path,  not by bold biosamples
	$(RUN) runoak --input $< query --output $@.bak --query "SELECT s.subject, SUBSTR(s.subject, INSTR(s.subject, ':') + 1) AS gold_path_id_int, s.object as inferred_env_local_scale, count(1) as path_count FROM entailed_edge ee JOIN statements s ON ee.subject = s.subject WHERE ee.predicate = 'rdfs:subClassOf' AND ee.object = 'GOLDTERMS:4212' AND s.predicate = 'mixs:env_local' group by s.object order by count(1) desc"
	cut -f1,2,3,5,6 $@.bak > $@
	rm -rf $@.bak

local/goldData_biosamples-inferred-soil-env_local_scale.tsv: local/goldData_biosamples.csv local/goldterms-env_local_scale-of-environmental-terrestrial-soil.tsv
	$(RUN) python -c "import pandas as pd; import sys; df1 = pd.read_csv(sys.argv[1]); df2 = pd.read_csv(sys.argv[2], sep='\t'); merged_df = pd.merge(df1, df2, left_on='BIOSAMPLE ECOSYSTEM PATH ID', right_on='gold_path_id_int', how='left'); merged_df.to_csv(sys.argv[3], index=False, sep='\t')" $(word 1,$^) $(word 2,$^) $@

local/goldData_biosamples-inferred-soil-env_local_scale-counts.tsv: local/goldData_biosamples-inferred-soil-env_local_scale.tsv
	cut -f19 $< | sed '1d' | sort | uniq -c | awk 'NR>1 {print $$2 "\t" $$1}' > $@ # NR>1 assumes there is an initial counts for an empty env_local_scale value

local/goldData_biosamples-inferred-soil-env_local_scale-ids.txt: local/goldData_biosamples-inferred-soil-env_local_scale-counts.tsv
	cut -f1 $< > $@
