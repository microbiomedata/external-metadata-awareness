# MIxS ontology translation
Translates MIxS information in the MIxS spreadsheets into an ontology.

The project uses venv to create a virtural enironment.
To create a virtual environment run the command python3 -m venv <environment name> .
I typically name my environment .env, and configure .gitignore to ignore .env files. This prevents the environment libraries from being uploaded to the repository.

After the environment is created, run the command source <environment name>/bin/activate to enter the environment.
Once in the environment, use pip to install libraries (e.g., pip install pandas). Once all the libraries have been installed you can export a list of them using the pip freeze command. Typically, the list is saved to a file named requirements.txt.
e.g., pip freeze > requirements.txt

To load a list of dependencies, use the pip instal -r command.
e.g., pip install -r requirements.txt

You exit the environment by executing the command deactivate in the terminal.
