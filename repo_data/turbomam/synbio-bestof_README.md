# synbio-bestof

This repo pulls together useful parts from various synthetic biology modeling repositories, especially with respect to the IARPA FELIX project. Will probably be renamed soon.

Usage notes:
- requires [Python Poetry](https://python-poetry.org/docs/#installation)
- requires an ssh tunnel and or database credentials: `ssh -L 1111:<dbhost>:5432 -o PreferredAuthentications=password -o PubkeyAuthentication=no <user>@<sshhost>.lbl.gov`
- ask a colleague for `felix-sheets-4d1f37aa312b.json` and place it in `local`
- Linux user? You may have to install system dependencies for `psycopg2`.
- `make install`
  - Linux user? You may see some warnings like `./utils/get-value.sh: 4: Bad substitution` and `utils/pgsql2sqlite.sh: 5: [[: not found
`. AFAICT, the make processes still work.
- `make all`
- `make synbio-all`
- optionally `make serve` to view the schema documentation
- optionally `make deploy` to push the documentation to GitHub Pages
  - this requires that you enable GitHub Pages and select the root of branch `gh-pages` as the source. 
  - this step will indicate the URL to browse for viewing your documentation


## Various FELIX data sources, schema generation, and data validation/conversion 


```mermaid
flowchart TD
    subgraph postgres [<b>Celnicker Lab Postgres DB</b>]
    tunnel[<i>Documents the known modifications, parts, elements.<br>Not all tables, columns, etc. are essential to this effort.<br>Access by tunneling through merlot.</i>]
    prod[(Prod = bicoid)]
    dev[(Dev = staufen)]
    end
    subgraph docs [<b>Celnicker Lab Documents</b>]
    gs[[Google Sheets]]
    xl[[XLSX documents]]
    end
    subgraph sstemplate [<b>Tabular Template</b>]
    ssnotes[<i>Google Sheets with access control<br>Does Celnicker lab want to contribute?</i>]
    end
    subgraph s [LinkML Schema]
    snotes[<i>Requires additional encoding<br>BLASTING of sequences<br>Making enumerations out of taxon strings</i>]
    end
    subgraph ds [<b>Schema-compliant datastore</b>]
    format_notes>JSON<br>SQLite<br>MongoDB<br>Back into Postgres?<br>Other RDBMS?>]
    end
    subgraph raw_subs [<b>Performer Submissions</b>]
    sub_notes[[<i>Documents the observed modifications<br>Many arbitrary formats<br>Can Josh or ORNL help make machine readable?</i>]]
    end

    subgraph sub_conv [Submission conversion process]
    conv_notes[/<i>Or initial colelction with DataHarmonizer?<br>Multiple templates for multiple inter-related classes<br>Ben Brown's ambitious suggestion:<br>Drawing tracks with modifications</i>/]
    end
    subgraph sub_score [Scoring submissions]
    score_notes[/<i>Diff of two schema-compliant datastores?<br>There are some dockerized solutions<br>with JSON output already</i>/]
    end
    postgres-- Export TSV<br>tsvs2linkml from schema-automator -->s
    sstemplate-- schemasheets -->s
    docs== These should mainly<br>be fed into Postgres ==>postgres
    postgres== <i>Export TSV?</i><br>linkml-convert<br><i>includes validation</i> ==>ds 
    s-..->ds
    docs-. Validation of<br>identifier discovery<br>with manual curations .->ds
    comp_subs>Schema-compliant<br>Performer submissions]
    sub_conv-- has input -->raw_subs
    sub_conv-- has output -->comp_subs
    sub_score-- has input -->comp_subs
    sub_score-- has input -->ds
```
