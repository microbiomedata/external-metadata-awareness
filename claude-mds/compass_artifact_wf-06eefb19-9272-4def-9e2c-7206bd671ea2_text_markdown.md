# Adding Your Ontology to EBI's OLS: A Complete Guide

**EBI's Ontology Lookup Service accepts ontologies through two distinct pathways—direct submission to OLS or through OBO Foundry registration—with each requiring a blend of rigorous technical preparation and extensive human interaction.** The process takes 2-6 months, demands OWL/RDF format compliance, automated ROBOT validation, and manual curator review, with acceptance depending on both technical quality metrics and community consensus about scientific value.

Getting an ontology into OLS involves navigating a sophisticated sociotechnical system where automated validation tools screen for technical compliance while human curators and community reviewers assess scientific merit, scope uniqueness, and alignment with community standards. The most significant challenge submitters face is the hybrid nature of requirements: you must satisfy both unforgiving automated quality checks and subjective human judgment about your ontology's value to the biomedical research community.

## Two pathways into OLS, each with distinct advantages

EBI offers two routes for getting your ontology indexed. **Direct OLS submission** involves emailing ols-submission@ebi.ac.uk with your ontology metadata in YAML format. The EBI SPOT team (Samples, Phenotypes and Ontologies Team) manually curates submissions to ensure quality and relevance. This path typically takes weeks to months without formal service-level agreements. You'll need to accept EBI's GDPR-compliant Submission Privacy Notice and provide comprehensive metadata including ontology PURL, title, description, preferred prefix, and various property URIs.

The alternative—and more prestigious—pathway is **OBO Foundry registration**. Ontologies registered with the OBO Foundry are automatically loaded into OLS nightly. This route provides a "quality seal" that signals adherence to community standards, but requires passing both automated quality checks and a multi-month community review process. The OBO Foundry Operations Committee makes acceptance decisions by consensus during their fortnightly meetings, with no single person able to unilaterally approve or reject submissions.

Strategic consideration matters here: **OBO Foundry membership grants automatic OLS inclusion plus higher community status**, with only ~100 ontologies achieving this designation compared to 266 total in OLS. Direct OLS submission offers faster turnaround but less recognition. For ontologies serving the broader biomedical research community, the OBO pathway is strongly recommended despite its longer timeline.

## Technical requirements demand OWL/RDF mastery and metadata completeness

The format requirements are strict and frequently trip up submitters. **OLS4 (the current version deployed October 2023) only supports RDF-serialized formats**—specifically OWL, OWL2, RDFS, and SKOS in RDF/XML, Turtle, N-Triples, or JSON-LD serializations. The traditional OBO flat file format is not directly supported and must be converted using the ROBOT tool before submission. Many submissions fail because ontologies are served with incorrect file extensions or missing content-type headers, causing the OLS parser to misidentify the format.

Your ontology file must contain at minimum an ontology declaration (`<http://www.example.org/ontology> rdf:type owl:Ontology`) and comprehensive Dublin Core metadata. **Required annotations include dc:title, dc:description, dc:creator, owl:versionInfo, owl:versionIRI, dcterms:license, and dcterms:issued/modified dates.** For updates, at least one of these version identifiers must differ from the previous version or loading will fail. SKOS vocabularies have additional requirements, needing annotations in a dedicated ConceptScheme individual.

The ROBOT tool (ROBOT is an OBO Tool) serves as the primary technical validation mechanism. ROBOT executes quality checks at three severity levels: ERROR (blocking issues), WARN (17 different check types including missing licenses, deprecated references, label formatting problems), and INFO (5 advisory checks). Common failures include missing_ontology_license, label_whitespace, duplicate_label, and illegal_use_of_built_in_vocabulary. You should run `robot report --input ontology.owl --output report.tsv` locally before submission to identify issues early.

For hosting, **stable PURLs (Persistent URLs) through http://purl.obolibrary.org/obo/ are strongly recommended** rather than direct GitHub links or institutional servers. The ontology must be publicly accessible via HTTP/HTTPS with proper redirects configured. Testing locally requires using file:/// paths correctly, which frequently confuses Windows users due to path formatting differences.

## Validation infrastructure catches format and quality issues automatically

OLS4 implements a sophisticated two-stage validation pipeline. Stage one validates RDF syntax and confirms the presence of ontology declarations—your file must parse correctly and contain the basic structural elements. Stage two executes a subset of OBO Foundry quality checks via ROBOT report, screening for metadata completeness, term definition quality, and adherence to naming conventions.

The validation system returns structured JSON responses with violation details at each severity level. **A critical limitation is that ROBOT validation currently doesn't work with non-OWL ontologies** (RDFS and SKOS vocabularies), causing confusion for submitters working with lightweight vocabularies. The system also validates import chains, and if your ontology imports external ontologies that have moved, changed format, or been deprecated, your entire submission will fail to load.

OBO Foundry principles operationalize additional technical requirements. **P1 (Open) demands openly available ontologies under permissive licenses**—CC0, CC-BY 3.0, or CC-BY 4.0 are required. P2 (Common Format) mandates at least one OWL product in valid RDF-XML accessible via official PURL. P3 (URI/Identifier Space) requires unique IRIs in the OBO namespace. P4 (Versioning) demands documented version control with proper owl:versionInfo and owl:versionIRI predicates. The OBO Dashboard at http://dashboard.obofoundry.org/ automatically checks conformance and displays results in a public matrix.

## Pain points cluster around format confusion and import failures

The most significant technical challenge submitters report is **file format detection ambiguity**. Many ontologies use the .owl extension for Turtle or JSON-LD files, not RDF/XML, but don't provide proper content-type headers. OLS4 defaults to RDF/XML when content-type is missing, causing parse failures. One developer noted: "Why does this work in Protégé and OLS3? Because OWLAPI literally bruteforce loads ontology files by trying every loader until it finds one which works." OLS4 abandoned this approach for performance reasons, making format specification critical.

Import dependency failures plague submissions. GitHub issue #453 documents extensive lists of failing imports across OBO ontologies, including broken links to DrugsNoChEBI_interactions_with_targets.owl, upheno.owl, and various cross-ontology imports. When your ontology imports terms from external ontologies, any failure in that import chain blocks your entire submission. You must ensure all imported ontologies are accessible, properly formatted, and maintain stable URLs.

The metadata complexity overwhelms first-time submitters. Understanding Dublin Core terms, managing version predicates correctly, and knowing which annotations are mandatory versus recommended requires ontology engineering expertise many domain scientists lack. SKOS vocabularies face additional hurdles with their special ConceptScheme structure requirements. **For updates, the strict requirement that owl:versionInfo, owl:versionIRI, or dcterms:modified must differ from previous versions** catches many submitters by surprise when updates fail to load.

Timeline uncertainty creates planning challenges. **The official guidance states reviews "can take any number of weeks or months, depending on the case at hand"** with a minimum expected response of 4 weeks. OBO Foundry reviews occur in order of dashboard compliance, not submission order, so fixing technical issues quickly impacts your queue position. The 2-month inactivity threshold means unresponsive submitters get marked inactive and must restart the process.

Local installation difficulties surface for users wanting custom ontology deployments. GitHub issues document IllegalArgumentException errors from improperly formatted file:/// URLs, especially on Windows systems. Custom ontologies appearing in OLS but not in the companion OXO (cross-reference service) require using unofficial Docker branches. The performance requirements also surprise users—large ontologies like NCBITAXON require ~22GB memory while default Docker configurations allocate only 4GB.

## Human review focuses on scope, community value, and collaboration

The social dimensions of OLS acceptance are as important as technical compliance. **For direct OLS submissions, the EBI SPOT team led by Helen Parkinson (parkinson@ebi.ac.uk) manually curates content** to ensure quality and relevance to the biomedical research community. While the criteria aren't fully published, curators assess whether the ontology serves genuine community needs, adheres to open access principles, and maintains sufficient documentation quality.

OBO Foundry submissions undergo more structured human review. After passing automated dashboard checks, a **NOR (New Ontology Request) Manager** assigns your submission to a reviewer from the Operations Committee on a rotating basis. Reviews are discussed at fortnightly Operations Committee meetings where community members can comment on GitHub issues. The assigned reviewer consolidates feedback into a checklist with MUST, SHOULD, and MUST NOT items using GitHub's checkbox syntax for tracking.

**Critical human-assessed criteria include scope uniqueness** (no overlap with existing OBO ontologies), evidence of use with documentation of actual users and applications, plurality of users demonstrating multiple stakeholders beyond a single project, and willingness to collaborate with related ontology maintainers. Reviewers verify you have a designated contact person who will remain responsive, a public issue tracker for community feedback, and evidence of coordination with similar ontologies. The scientific accuracy of terms gets assessed by domain experts within the review process.

The Operations Committee makes acceptance decisions by **consensus without requiring quorum**, with three possible outcomes: acceptance, rejection, or inactive status. This consensus model means no single gatekeeper can fast-track your submission, but also ensures no individual can arbitrarily block a submission the community supports. Community endorsement through citations, documented users, and collaboration letters significantly influences acceptance even though these aren't formally required.

Contact points are well-defined: **ols-submission@ebi.ac.uk serves as the primary direct submission channel** requiring GDPR privacy notice acceptance. For general support use ols-support@ebi.ac.uk. OBO Foundry submissions go through GitHub at https://github.com/OBOFoundry/OBOFoundry.github.io/issues using the New Ontology Request template. The community maintains active mailing lists (obo-discuss, obo-operations-committee) and a Slack workspace for collaboration.

## Social requirements demand community engagement and collaboration evidence

**You cannot submit a single-purpose, single-user ontology and expect acceptance.** The review process explicitly checks for plurality of users and evidence of community value. This means before submission you should document who uses your ontology, what applications implement it, which publications reference it, and what community need it addresses that existing ontologies don't meet.

The orthogonality requirement poses significant hurdles for some domains. OBO Foundry demands ontologies be orthogonal—no domain overlap with existing registered ontologies. If your proposed scope overlaps significantly with an existing ontology, reviewers will request you demonstrate good faith effort to work with that ontology's maintainers or provide strong justification for why a separate ontology is necessary. This can lead to requests for collaboration, scope narrowing, or outright rejection.

Proactive community engagement before submission helps tremendously. Users report that joining the obo-discuss mailing list, participating in community discussions, presenting at ICBO (International Conference on Biomedical Ontology) or OBO community calls, and coordinating with related ontology developers before formal submission significantly improves acceptance chances and speeds the process. The OBO Slack workspace enables informal discussions that can resolve potential conflicts before they become formal objections.

## Development tools and best practices streamline the process

**Using the Ontology Development Kit (ODK) from the start automatically generates required metadata files** stored under src/metadata/, including both OBO registry entries and PURL configuration files. This dramatically simplifies the submission process and prevents common metadata errors. The ODK templates incorporate OBO Foundry principles by default, ensuring compliance from the beginning rather than requiring retrofitting.

For format conversion and validation, ROBOT provides essential functionality. Key commands include `robot convert --input ontology.obo --output ontology.owl` for format conversion, `robot report --input ontology.owl --output report.tsv` for validation, and `robot reason --input ontology.owl --reasoner ELK --output reasoned.owl` for reasoning and consistency checking. You can create custom ROBOT report profiles that adjust violation levels or add SPARQL-based validation queries specific to your domain.

Version management requires discipline. Maintain version history, use semantic versioning, tag releases in version control, and keep old versions accessible. The owl:versionIRI should include the version number (e.g., http://example.org/ontology/1.0.0) and change with each release. Testing locally before submission using the `./dev-testing/teststack.sh ./testcases ./testcases_output` workflow from the OLS4 repository catches many issues before formal submission.

## Timeline expectations require patience and early preparation

Conservative timeline estimates for **direct OLS submission range from weeks to months** without published service-level agreements. The EBI team handles submissions on a case-by-case basis with response times varying by complexity, current workload, and how completely you've provided required metadata.

**OBO Foundry registration typically requires 3-6 months total**: automated dashboard review takes days to weeks depending on how many errors you must fix, human review queuing happens in compliance order rather than submission order, the formal review process itself takes 2+ months typically, and the inactivity threshold kicks in at 2 months of non-response from submitters. Original submission dates are honored for priority, so early engagement helps even if your ontology isn't initially compliant.

Accelerating factors include pre-conformance to OBO principles before submission, complete and accurate documentation, evidence of existing community use, proactive communication with reviewers, and absence of term conflicts with existing ontologies. Users report the process works smoothly when ontologies are designed from the start with OBO principles in mind rather than trying to retrofit compliance later.

## Architecture and operational details matter for understanding the system

OLS4 replaced OLS3 in October 2023 with a fundamentally different architecture. **The new system uses Neo4j 4.4.x for graph queries and Apache Solr 9.0.0 for full-text search**, with ontologies converted from RDF into JSON and CSV datasets through a seven-stage ETL pipeline. The dataload process is 16x faster than OLS3, taking only 6% of the previous time, though complete OBO library loads still require several hours.

The system implements full OWL2 specification support including property chains, disjointness axioms, and annotations on annotations. **OLS4 serves 50 million requests from 200,000 unique hosts** (November 2023-February 2024 data), with backward-compatible API maintaining OLS3 endpoints while adding new capabilities. The platform supports full internationalization with ontologies browsable in multiple languages using rdfs:label with language tags.

Technical integration with BioRegistry enables compact URI resolution harmonized with identifiers.org. Cross-ontology references display tags showing the defining ontology for imported terms. The system maintains both production and development environments, with ontologies first loaded into dev for testing before production deployment.

## Conclusion: Success requires balancing technical rigor with community integration

Adding an ontology to EBI's OLS demands mastery of two distinct skillsets that many domain scientists find challenging to combine. You must achieve technical excellence in OWL/RDF formatting, metadata specification, and validation compliance while simultaneously demonstrating community value, collaborating with existing ontology maintainers, and engaging in the social processes of scientific community governance.

**The fundamental insight many submitters miss is that OLS operates as a curated repository, not an open platform.** The extensive technical requirements serve as a quality filter, but passing automated validation only qualifies you for human review where subjective assessments of scientific value, community need, and collaboration potential determine acceptance. This dual-gated process ensures OLS maintains high quality while requiring submitters to invest substantially more effort than simply uploading a file.

The most successful strategy involves designing your ontology from inception with OLS/OBO principles in mind, using the Ontology Development Kit for automated compliance, engaging the community early through mailing lists and Slack, documenting users and use cases throughout development, and budgeting 3-6 months for the submission and review process. The effort investment is substantial, but acceptance into OLS provides your ontology with professional infrastructure, automatic updates, community visibility, and integration with the broader ecosystem of biomedical ontology tools that would be impractical to implement independently.