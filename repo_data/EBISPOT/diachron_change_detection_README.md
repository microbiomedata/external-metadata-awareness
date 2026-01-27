detection_repair_maven
======================

Maven Project with services which correspond on the Change Detection and Validation/Repair Modules 

Configurations Notes
=====================
Folder Config Files contains two sample configuration files
 - change detection parameters for multidimensional model (md_config.properties)
 - change detection parameters for ontological model (config.properties)

If someone plans to use a diferrent virtuoso triple store to store the diachron dataset versions, then the repository fields (i.e., Repository_IP, Repository_Username etc.) should change w.r.t. the Virtuoso setting. 

All the detected changes between two dataset versions e.g., v1, v2 are stored in a dedicated named graph. This is a difference from the previous version of the algorithm which stored all the detected changes for all the dataset evolutions in a single named graph which was denoted by Changes_Ontology field in the properties file. In the new version of the algorithm, in the properties file we define the Dataset_Uri which is connected with the dataset versions and is also used to represent the changes ontologies. Such meta-data are stored in a named graph called http://datasets. For instance, consider the efo datasets. It holds that Dataset_Uri=http://www.ebi.ac.uk/efo/ and we can find the triples:
 - <http://www.ebi.ac.uk/efo/> rdfs:member <http://www.diachron-fp7.eu/resource/recordset/efo/2.34>
 - <http://www.ebi.ac.uk/efo/> rdfs:member <http://www.diachron-fp7.eu/resource/recordset/efo/2.35>
 - ...
As a result, given the Dataset_Uri, we can find all its corresponding dataset versions which are stored into the corresponding named graphs within Virtuoso. We follow a similar approach to create the changes ontologies as well. Back in the case of efo datasets, consider the versions http://www.diachron-fp7.eu/resource/recordset/efo/2.34, http://www.diachron-fp7.eu/resource/recordset/efo/2.35. The change detection process will create the changes ontology: http://www.ebi.ac.uk/efo/changes/2.34-2.35. The following meta-data triples into named graph http://datasets: 
 - <http://www.ebi.ac.uk/efo/changes> rdfs:member <http://www.ebi.ac.uk/efo/changes/2.34-2.35>
 - <http://www.ebi.ac.uk/efo/changes/2.34-2.35> co:old_version <http://www.diachron-fp7.eu/resource/recordset/efo/2.34>
 - <http://www.ebi.ac.uk/efo/changes/2.34-2.35> co:new_version <http://www.diachron-fp7.eu/resource/recordset/efo/2.35>

Moreover in our Virtuoso, we have stored the definition of changes in a separate named graph whish is denoted by the field Changes_Ontology_Schema. Again, if someone plans to use a different triple store, make sure to import the ontology of change definitions before the change detection process. The corresponding files for both the ontological model and multidimensional can be found in folder: Changes_Ontology_Schema. Moreover, he has to create the http://datasets named graph to store the meta-data for both the datasets and the change detections. 

Finally field Simple_Changes_Folder refers on tomcat-accessible folder which contains the SPARQL query templates which will be used for the change detection process. This field has to be changed to a new accessible path w.r.t. the new deployment setting of each data pilot. 

Module Setup and Deployment
===========================
The modules are created as maven projects using Netbeans 7.0.1. The created war file (ForthMaven-1.0.war) is located in folder target and it was built w.r.t. the configuration file config.properties and it was tested successfully on a Tomcat Server 7.0.54 (Windows 7). Folder src/main/java/clients contains some small client files which test all the functionalities of both the Change Detection and the Validation/Repair modules. 

The pom file contains all the dependencies which can be downloaded from the central Maven repository. However, there are two external dependencies which have to be manualy imported. The corresponding jar files can be found in folder: Libraries and  the commands to import them in the local Maven repository can be found in file installJars.bat.

