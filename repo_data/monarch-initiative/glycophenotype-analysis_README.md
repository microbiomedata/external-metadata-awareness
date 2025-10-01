### Analysis for the Glycophenotype paper
 
A set of jupyter notebooks for generating figures in the Glycophenotype paper.
 
Instructions are included to run owlsim using docker so that the analysis is fully
reproducable (other than random sampling). Test it by turning off your network
connection after setting up your python environment.


#### Getting Started

Set up with your favorite python virtual environment, for example:

    virtualenv -p /usr/bin/python3.6 venv
    source venv/bin/activate
    pip install -r requirements.txt
    juypter notebook
    
Running docker:

    # Build the image
    cd owlsim-docker
    docker build -t owlsim-slim .

    # Run and wait 90 seconds for the server to start up
    docker run -d -p 9031:9031 --name owlsim owlsim-slim
    
    # Example comparison
    # http://localhost:9031/compareAttributeSets?a=HP:0002079&a=HP:0010804&a=HP:0010539&b=HP:0006989&b=HP:0000219&b=HP:0000248

    # stop the container
    docker stop owlsim
