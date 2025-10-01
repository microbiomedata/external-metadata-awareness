# Science awards analysis

See results:

 * [results/science-awards-summary.tsv](results/science-awards-summary.tsv)

There should be one row for every award in Wikidata

For each award, we breakdown the number of awardees by gender. We also
do a binomial test for bias. This is not yet broken down by dates of
award. As expected awards that started earlier display worse bias.

Example:

|AWARD|DESCRIPTION|female|male|non-binary|transgender female|p_value|start_date|end_date|PERSON|
|---|---|---|---|---|---|---|---|---|---|
|Benjamin Franklin Award|$null$|1.0|14.0|0.0|0.0|0.0004882812499999999|2002-01-01T00:00:00Z|2016-01-01T00:00:00Z|Alex Bateman; Ben Langmead; Ewan Birney; Helen M. Berman; Heng Li; Jim Kent; Jonathan A. Eisen; Lincoln Stein; Michael Ashburner; Michael Eisen; Owen White; Philip Bourne; Robert Gentleman; Sean Eddy; Steven Salzberg|

This recapitulates known problems, see e.g.
[The "Ben Franklin Award for Open Access in the Life Sciences" should be renamed as a "#Manward"](https://phylogenomics.blogspot.com/2019/03/the-ben-franklin-award-for-open-science.html)

## Methods

See [Makefile](Makefile}

We use sparqlprog to query a list of all award-awardee pairs from Wikidata, along with date of award

The python script in [src](src) uses pandas to summarize this
