# automaxoviewer

automaxoviewer is a JavaFX graphic user interface application designed to streamline creating
annotations for the [Medical Action Ontology](https://pubmed.ncbi.nlm.nih.gov/37963467/) by simplifying
curation of the output of the [automaxo](https://github.com/monarch-initiative/automaxo) project.

## Installation

Prerequisites for running automaxoviewer are Java 21, which can be downloaded 
at the [Azul zulu](https://www.azul.com/downloads/) and other locations, as well as
[apache maven](https://maven.apache.org/), which is required to run the app. 

To install the program, download the source code from this GitHub repository with the following command
```
git clone https://github.com/monarch-initiative/automaxoviewer.git
```
If you do not have git installed, it is also possible to download a ZIP archive of the program and unpack it locally.

## Running the program

To run the program, cd into the automaxoviewer directory and enter the following command.
```
mvn javafx:run
```
After a few seconds, the GUI will appear. 

See also the online documentation at https://monarch-initiative.github.io/automaxoviewer/.
