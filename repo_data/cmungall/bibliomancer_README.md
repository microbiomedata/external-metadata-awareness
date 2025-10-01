# bibliomancer

Performs magic on bibliographies

Vision:

- bibliography management based on well-defined datamodels and clearly specified schema/ontology mappings
- Automated inference of missing metadata

Current implementation

- Currently only works for paperpile CSV exports
- Has some missing metadata inference (e.g. DOIs from pre-print URLs, PMC from PMID)
- Export to markdown via jinja templates for exporting CVs etc
