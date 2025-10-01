# Phenopacket-Scraper-Webapp

A web application that utilizes phenopacket-scraper-api to provide a demonstration portal for users to select a target for scraping and to view or export the resulting phenopacket.


##Setup:

To get the project's source code, clone the github repository:

    $ git clone https://github.com/monarch-initiative/phenopacket-scraper-webapp.git

Install VirtualEnv using the following:

    $ [sudo] pip install virtualenv

Create and activate your virtual environment (with python 3):

    $ virtualenv venv
    $ source venv/bin/activate

Install all the required packages:

	$ venv/bin/pip install -r requirements.txt

Create your database and the superuser by running this from the `pps_webapp/` directory of the repository:

	$ python manage.py migrate
	$ python manage.py createsuperuser

Setup phenopacket-scraper api by following instructions from this repository:
- https://github.com/monarch-initiative/phenopacket-scraper-api

##Usage

To run the server enter the following in the `pps_webapp/` directory of the repository

	$ python manage.py runserver

Run the phenopacket-scraper-api in a different port by entering this in `phenopacketscraper/` directory of the API repository:

	$ python manage.py runserver localhost:8001

Now you can go to your browser and test it using:

	http://localhost:8000/