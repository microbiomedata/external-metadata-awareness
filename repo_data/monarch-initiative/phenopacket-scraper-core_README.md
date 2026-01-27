=================
Phenopacket-scraper-core
=================

Extracts information from life-science websites and texts, generating phenopackets with the extracted information and correct external ontology references.


=================
 Running PhenopacketScraper Tool
=================

Setup
-----

To get the project's source code, clone the github repository:

::

  $ git clone https://github.com/monarch-initiative/phenopacket-scraper-core.git

First, you need to create a virtual environment and activate it.

::

  $ [sudo] pip install virtualenv
  $ virtualenv -p python3 venv
  $ source venv/bin/activate
  (venv)$ 

Next, install all the dependencies in the environment.

::

  (venv)$ venv/bin/pip install -r requirements.txt

Clone the phenopacket-python repository:

::

  $ git clone https://github.com/phenopackets/phenopacket-python.git

Install it in your virtual environment:

::

  (venv)$ cd phenopacket-python
  (venv)$ python setup.py install

Add this to the end of ~/.profile or ~/.bash_profile file to add phenopacket-python directory to your python environment variables:

::

  $ export PYTHONPATH=$PYTHONPATH:[path of phenopacket-python directory]

For Example:

::

  $ export PYTHONPATH=$PYTHONPATH:/Users/Gauss/Home/phenopacket-python

Now, install the application into the virtual environment.

::

  (venv)$ cd phenopacket-scraper-core
  (venv)$ python setup.py install

Usage
-----
::

  (venv)$ pps --help
  (venv)$ pps scrape -u (url)

Example:

::

  (venv)$ pps scrape -u http://molecularcasestudies.cshlp.org/content/early/2016/02/09/mcs.a000786.abstract
  (venv)$ pps -q scrape -u (Url)

  Title: Mutations in the substrate ...

  Abstract:
  We describe a large Lebanese fa...

  HPO Terms:
  Diffuse cerebellar atrophy
  Generalized hypotoni...


To use files with list of URLs as input:

::
  
  (venv)$ pps scrape -f (Filename)

Example:

::

  (venv)$ pps scrape -f testurls.txt

  testurls.txt:

  http://molecularcasestudies.cshlp.org/content/early/2016/02/09/mcs.a000786.abstract
  http://molecularcasestudies.cshlp.org/content/2/2/a000703.abstract
  http://molecularcasestudies.cshlp.org/content/2/2/a000620.abstract
  http://molecularcasestudies.cshlp.org/content/2/1/a000661.abstract


To scrape required data from a HTML file:

::

  (venv)$ pps scrape -d (Filename)

To store the output in a file:

::

  (venv)$ pps scrape -u (Url) -o (Filename)
  (venv)$ pps scrape -d (Filename) -o (Filename)
  (venv)$ pps scrape -f (Input_filename) -o (Output_filename)

This will create two files for now, (Filename)_abstract.txt will contain the abstract and the (Filename)_hpo_terms.txt will contain the hpo terms.


Sci-graph Annotation:

::
  
  (venv)$ pps annotate -u (url)
  
  [{u'start': 4, u'token': {u'terms': [u'TORC1 complex'], u'id': u'GO:0031931', u'categories': [u'cellular component']}, u'end': 10}, {u'start': 11, u'token': {u'terms': [u'inhibitor'], u'id': u'CHEBI:35222', u'categories': [u'chemical role']}, u'end': 20}, {u'start': 72, u'token': {u'terms': [u'multiple'], u'id': u'PATO:0002118', u'categories': [u'qua......
  
  HPO Terms:
  Neoplasm
  Breast carcinoma
  Carcinoma
  increased carcinoma incidence

Phenopacket Generation:

::

  (venv)$ pps phenopacket -u (url)
  (venv)$ pps phenopacket -d (html_filename)

  {
  "entities": [
    {
      "id": "http://molecularcasestudies.cshlp.org/content/2/1/a000661.abstract",
      "type": "paper"
    }
  ],
  "id": "gauss-packet",
  "phenotype_profile": [
    {.....


To store the output in a file:

::

  (venv)$ pps annotate -u (Url) -o (Filename)
  (venv)$ pps phenopacket -u (Url) -o (Filename)




Cleaning Up
-----------

Finally, when done, deactivate your virtual environment::

  (venv)$ deactivate
  $
