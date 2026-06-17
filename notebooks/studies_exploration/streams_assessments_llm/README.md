# streams_assessments_llm/

LLM-assisted assessment of how well stream/river microbiome manuscripts meet
reporting standards, for the **STREAMS** initiative (Standards for Technical
Reporting in Environmental and host-Associated Microbiome Studies,
streamsmicrobiome.org; built on the STORMS checklist). Led by Julia Kelliher;
the main manuscript is in revision at Nature Microbiology and a dedicated
"STREAMS LLM paper" is in progress. Tracked in issue #67.

(Renamed from `streams_assesments_llm` — fixed typo.)

The actual extraction is a manual Claude-in-browser workflow (see `notes.txt`
and `claude_3.5_sonnet_prompt*.txt`); the notebooks are the automatable
bookends:

| Notebook | What it does |
|---|---|
| `streams_prep.ipynb` | NMDC study API + CrossRef + the STREAMS Google Sheet -> input TSVs (incl. `streams_final.tsv`). |
| `fetch_pdf_from_unpaywall.ipynb` | Resolve DOIs to open-access PDFs via Unpaywall. |
| `aligning_pdf_filenames_and_dois.ipynb` | TF-IDF match of DOI metadata to PDF filenames. |
| `streams_results_summarizer.ipynb` | Aggregate the per-PDF Claude result TSVs (`claude_3.5_sonnet_results/`) into summary tallies. |

**Rerun when:** assessing a new batch of manuscripts against the STREAMS
reporting standards.
