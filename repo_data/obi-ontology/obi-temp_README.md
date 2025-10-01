= Ontology for Biomedical Investigations Release 2016-10-11 =

Date of Release: 2016-10-11

Subversion Revision: 4083

== Access ==

* This version in OWL format: http://purl.obolibrary.org/obo/obi/2016-10-11/obi.owl
* This release directory in Subversion: https://sourceforge.net/p/obi/code/HEAD/tree/releases/2016-10-11/
* Latest Version in OWL format: http://purl.obolibrary.org/obo/obi.owl
* Latest Version in OBO format: http://purl.obolibrary.org/obo/obi/obi.obo
* Browse Latest Version: http://purl.obolibrary.org/obo/obi/browse
* All Releases: http://obi-ontology.org/page/Releases
* Issue Tracker: http://purl.obolibrary.org/obo/obi/tracker

Please see the Tutorials for instructions on downloading and viewing: http://obi-ontology.org/page/Tutorials

== Release Files ==

* obi.owl: the main OBI file in Web Ontology Language (OWL) XML format
* obi_core.owl: a version with the OBI Core terms
* obi_iedb.owl: a version of OBI using IEDB's alternative terms for labels
* obi_isa.owl: a version of OBI using ISA's alternative terms for labels

* branches: OBI development files used to build the release
* external: IAO and BFO files used to build the release
* docs: reports on the release files, for example:
** newIDs.tab: a list of terms added since the last release
** obi.txt: report on term types and source ontologies
** obi.tsv: a list of all the terms in obi.owl

This release candidate was built using revision 4083 of the new OBI build tools:

http://sourceforge.net/p/obi/code/HEAD/tree/trunk/src/tools/build/

== New in this Release ==

There are 14 new classes since the last release:

* OBI:0002110 digital object identifier
* OBI:0002111 enhanced cross-linking immunoprecipitation high-throughput sequencing assay
* OBI:0002112 small RNA-seq
* OBI:0002113 bromouridine labeling and sequencing
* OBI:0002114 bromouridine pulse-chase and sequencing
* OBI:0002115 cytometry time of flight assay
* OBI:0002116 high performance liquid chromotography assay
* OBI:0002117 whole genome sequencing assay
* OBI:0002118 exome sequencing assay
* OBI:0002119 microscopy assay
* OBI:0002120 mixed lymphocyte reaction assay
* OBI:0002121 killer cell immunoglobulin-like receptor typing assay
* OBI:0002122 major histocompatibility typing assay
* OBI:0200001 geometric mean calculation

== Known Issues ==

In the course of preparing OBI Core we have made significant changes to many of OBI's upper-level terms. However we have not yet had time to revise all the children of the changed nodes. In particular, many of the descendants of "measurement data item" have not yet been revised to use the new "value specification" approach.

If you have any questions, please ask on the developer mailing list at http://groups.google.com/group/obi-developer

== About the Ontology for Biomedical Investigations ==

The Ontology for Biomedical Investigations (OBI) project has developed an integrated ontology for the description of biological and clinical investigations. This includes a set of 'universal' terms, that are applicable across various biological and technological domains, and domain-specific terms relevant only to a given domain. This ontology supports the consistent annotation of biomedical investigations, regardless of the particular field of study. The ontology represents the design of an investigation, the protocols and instrumentation used, the material used, the data generated and the type analysis performed on it. OBI is being built under the Basic Formal Ontology (BFO) and imports terms from OBO foundry ontologies. OBI also reflects domains specific extensions which were merged into obi.owl. These include terms merged into obi.owl from the Immune Epitope Database Ontology (www.ideb.org) and community suggested terms from many communities.

Aims:

* Develop an Ontology for Biomedical Investigations in collaboration with groups representing different biological and technological domains involved in Biomedical Investigations
* Make OBI compatible with other bio-ontologies
* Develop OBI using an open source approach
* Create a valuable resource for the biomedical communities to provide a source of terms for consistent annotation of investigations

More details at: http://purl.obolibrary.org/obo/obi

Further reading: You can find the OBI manuscript which this version supports at http://purl.obolibrary.org/obo/obi/repository/trunk/docs/papers/release/Manuscript.doc

== Ontology Development ==

OBI Ontology Development is collaborative, term suggestions and new community representatives are welcome. Single term can be suggested via the OBI tracker http://purl.obolibrary.org/obo/obi/tracker

If you represent a community and/or have many terms to suggest please email OBI Developers <obi-devel@lists.sourceforge.net> with details. If you would like to see the latest development version please check out the development copy of OBI from sourceforge.

Tutorials on how to do this can be found here: http://obi-ontology.org/page/Tutorials

The OBI wiki can be found at: http://obi-ontology.org

== How to Contact Us ==

Send emails with questions on how to use OBI to obi-users@googlegroups.com. You
can sign up for this group, or view the archives, at:
http://groups.google.com/group/obi-users

Discussion among OBI developers can be found at obi-devel@lists.sourceforge.net. You can sign up for this group, or view the archives, at:
https://lists.sourceforge.net/lists/listinfo/obi-devel or
http://groups.google.com/group/obi-developer

OBI term requests, as well as reports of bugs or other issues can be
entered in our tracker: http://purl.obolibrary.org/obo/obi/tracker The
tracker currently requires you to have or sign up for a sourceforge
account. Please send an email to obi-users@googlegroups.com if this is
problematic.


Release notes author: James A. Overton <james@overton.ca>

