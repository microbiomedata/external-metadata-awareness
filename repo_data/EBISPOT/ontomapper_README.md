#+TITLE: Ontomapper utility
#+AUTHOR: Warren Read
#+STARTUP: showall indent
#+OPTIONS: num:nil toc:nil


Ontology mapper command-line utility, in Python

** Overview

This Unix command-line utility enables you to take the GWAS spreadsheet as input
and process it with OxO (using either the public or internal EBI web service, as
you wish, depending on your access level) to enrich it with terms from
ontologies other than the default (EFO). You can optionally include other
ontologies in extra rows or extra columns, and can further choose whether to use
one column per output ontology, if you want to retrieve matching terms from
multiple ontologies other than EFO. You may also choose whether to retain or
dispense with the original EFO terms in the output.

** Dependencies

Python 3.6 and above. Some of the imported libraries come as standard with a
Python 3.6 distribution; if not, your (virtual) environment may need to reflect
this. Non-default libraries and their requisite versions are listed in
~requirements.txt~; assuming the latter is in the default directory, you should
download these packages using the following command:

#+BEGIN_SRC sh
  $ pip3 install -r ./requirements.txt
#+END_SRC

** Installation

Just ~git clone~ this project, from ~master~, or ~dev~ if you're feeling only
very slightly more adventurous: in either case, you will be able to execute the
python script from the top-level working directory.

** Execution

The main script is ~ontomapper.py~: simply execute this with all necessary
switches (as described below), and redirect standard output to generate your
output file, containing the new ontology terms that you requested. The easiest
way is to specify the provided config file (~./ontomapper.ini~, or your own
customised copy thereof) as the argument to the ~--config~ switch, and then
override any of the default values you don't want, directly, with further
command-line switches. Command-line switches always take precedence over any
corresponding values in the config file, but missing parameters (if you don't
provide either a config file or /all/ of the relevant command-line switches)
will cause the program to abort. Informational progress reports get printed to
standard error (usually the console).

There are several switches available: most have a default value set, either in
the executable itself, or in the config file, ~ontomapper.ini~; all switches
have one-letter shortcuts too, which you can see in the program help menu (just
try to run the program without any switches---or just ~--help~ on its own---to
view this). The currently active options, that you may wish to specify
explicitly, and do not have to place in any particular order, are as follows
(all of these have default values too, which you may opt to leave
unchanged---just remember to specify a config file on the command line):

1. ~--config ontomapper.ini~ /(default config, provided)/: config file in ~.ini~
   format, containing default values for other switches;
2. ~--input-file ./gwas_subset.tsv~ /(example file, provided herewith)/:
   filepath or URL specifying location of input spreadsheet, one column of which
   should contain source ontology terms;
3. ~--format~ [ ~csv~ | ~tsv~ ]: text format of spreadsheet file (2 options only
   at present);
4. ~--layout~ [ ~in-situ~ | ~uni-row~ | ~multi-row~ | ~uni-column~ |
   ~multi-column~ ]: choice of how terms from new ontologies are stored in the
   output spreadsheet, as described below:

   | option         | effect                                                                                                                                                                                                                                              |
   |----------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
   | ~in‑situ~      | Do not increase the number of rows or columns to house any new ontology terms---simply append them to the list existing EFO terms, in the same cell.                                                                                                |
   | ~uni‑row~      | Add an extra row to accommodate new ontology terms---all new terms, from any ontology in the target list, appear in the same cell, while other cells in the new row are copied from the row containing the source EFO terms.                         |
   | ~multi‑row~    | Add one new extra row per target ontology (if there are any hits)---terms from each target ontology appear together in a dedicated, newly-generated row, while other cells in the new rows are copied from the row containing the source EFO terms. |
   | ~uni‑column~   | Add an extra column to accommodate new ontology terms---all new terms, from any ontology in the target list, appear in the same cell.                                                                                                               |
   | ~multi‑column~ | Add one new extra column per target ontology---terms from each target ontology appear together in a dedicated, newly-generated column.                                                                                                              |

5. ~--column-index~: zero-based int index of column holding source ontology
   terms (mutually excludes ~column-name~);
6. ~--column-name~: title or header of column holding source ontology terms
   (mutually excludes ~column-index~);
7. ~--keep~ | ~--no-keep~: whether to retain the original EFO terms in the
   output spreadsheet---choosing ~--no-keep~ can mean dropping the original row,
   dropping the original column, or both, depending the value of the ~--format~
   switch and whether the EFO terms are mappable or not;
8. ~--target ncit mesh doid~ /(example list)/: new ontology, or ontologies, to
   include in the output spreadsheet---supply the switch itself once only,
   followed by a single ontology or a space-separated list;
9. ~--distance~: stepwise OxO distance (ontology to ontology), taking integer
   values between 1 and 3 inclusive, where the greater the distance, the greater
   the number of hits returned (necessarily so, because the set of hits at
   distance = 2 includes hits with distance = 1, and so on);
10. ~--oxo-url~: URL of the OxO web service---internal EMBL/EBI users may
    sometimes wish to use a development server, for example;
11. ~--number~: HTTP requests involving large numbers of query terms should be
    chunked---specifies maximum number of individual query terms per request;
12. ~--verbose~ | ~--quiet~: whether to print a flood of program progress data
    and reports, or keep it simple;
13. ~--mapping-file~: filepath for optionally outputting list of source to
    target term mappings;
14. ~--version~: show program's version number and exit.

Remember that single-letter shortcuts for all the above switches are available
from the program help menu.

The other significant script here is ~spreadsheet_sampler.py~: this can be used
to generate a subset of records and fields from a master spreadsheet, like the
[[https://www.ebi.ac.uk/gwas/api/search/downloads/alternative][public-domain GWAS spreadsheet]]; this enables easy experimentation with
~ontomapper.py~ itself, using the smaller genenerated spreadsheet as input. An
example of such a smaller generated spreadsheet is provided here in the form of
~gwas_subset.tsv~, so it should not be strictly necessary to run
~spreadsheet_sampler.py~ at all. If you do wish to run it however, it has its
own help system; this can be viewed by invoking ~spreadsheet_sampler.py~ without
any parameters or switches.

*** Examples

To obtain equivalent terms from both MeSH and the Disease Ontology, using the
public web service, reserving a new column for each new ontology and dispensing
with the original EFO terms, you can enter the following command (assuming you
have 'execute' privilege on ~ontomapper.py~), redirecting output to a new
tab-separated-variable (spreadsheet) file:

#+BEGIN_SRC sh
  $ ./ontomapper.py --config ontomapper.ini --target mesh doid --layout multi-column --no-keep > gwas_new.tsv
#+END_SRC

To do something equivalent, taking as input the provided GWAS spreadsheet subset
sample, and this time using one-character switch shortcuts:

#+BEGIN_SRC sh
  $ ./ontomapper.py -g ontomapper.ini -i gwas_subset.tsv -t mesh doid -l multi-column -d > gwas_new_subset.tsv
#+END_SRC

To obtain a list of current EFO->MeSH mappings only, without generating a full
'replacement' GWAS spreadsheet containing the mapped terms:

#+BEGIN_SRC sh
  $ ./ontomapper.py --config ontomapper.ini --mapping-file efo_mesh_mappings.tsv --target mesh > /dev/null
#+END_SRC

Note that although the last option above implicitly takes default values for
most parameters, in this case the output is unaffected by these defaults,
because it is effectively an intermediate file in the standard pipeline which is
desired, rather than the usual endpoint (i.e. a full version of the GWAS
spreadshet, with mapped ontology terms).

Look at ~ontomapper.ini~ for default values of other parameters, any or all of
which can be changed in the config, or overridden on the command line.
