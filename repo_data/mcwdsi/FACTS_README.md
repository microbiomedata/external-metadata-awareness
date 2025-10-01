# FACTS
Florida Annotated Corpus for Translational Science

##Directory descriptions

**BRAT:** Contains the configuration files for running the BRAT annotation tool and the SPARQL queries used for extracting class names and hierarchies from the ontologies used in the FACTS project in order to configure BRAT.

&nbsp;&nbsp;**data:** Contains one folder per ontology used in the annotations. Each folder contains the configurations files for BRAT.

&nbsp;&nbsp;**work:** Contains one folder per ontology used in the annotations. Each folder contains the normalization database files for BRAT.

**Corpus_files:** Contains the FACTS corpus files.

&nbsp;&nbsp;**annotated\_corpora:** Contains the goldstandard corpus files.

&nbsp;&nbsp;**clean_corpora:** Contains the corpus files with the `.txt` and `.ann` extensions to be used in BRAT. The text files are copies of the files under `raw_corpora/corpus_txt_only/`.

&nbsp;&nbsp;**raw\_corpora:** Contains the source files for the FACTS corpus. PDFs, raw text files (under `corpus_txt_all/`), cleaned-up text files (under `corpus_txt_only/`), and folders with FACTS corpus files (`.txt`) with their respective annotation (`.ann`) files. The latter folders are to be copied in each of BRAT's `data/<ONTO>` directory to create separate annotation files per ontology.

**OWL:** Contains the OWL files used in the project.


	  FACTS
		|__BRAT
		|	|
		|	|__data
		|	|	|__...
		|	|
		|	|__work
		|		|__...
		|		
		|_Corpus_files
		|		|
		|		|__annotated_corpora
		|		|	|
		|		|	|__VSO
		|		|		|__VSO_corpus_goldstandard
		|		|
		|		|__clean_corpora
		|		|		|__hypertension_1
		|		|		|__hypertension_2
		|		|		|__testcorpus_1
		|		|		|__testcorpus_2
		|		|
		|		|__raw_corpora
		|				|
		|				|__corpus_pdf
		|				|		|__...
		|				|
		|				|__corpus_txt_full
		|				|		|__...
		|				|
		|				|__corpus_txt_only
		|						|__...
		|
		|_OWL

