# biosamples-facet-concurrence

## About

BioSamples is an EBI database that accepts biological sample meta data from many sources and acts as a central hub and connector to other databases such as ENA/ArrayExpress/PRIDE. While some of these sources explicitly define required and suggested parameters, BioSamples has no submission requirements and therefore contains a very diverse noSQL database. There are about 25 K facets across 4-5 M samples. I'm diggining into what is in the database with statistical learning to uncover automated curation oppotunities and data analysis.

Code to extract all the samples from the BioSamples db via the API and count concurrence between keys (aka facets). I am looking for facets that co-occur within samples the most in order to begin a key prediction network.

## Process

1. Get the facets for every sample in the db. This is done using a multithreading python script Biosamples-multithreading-crawler.py.
2. Get a list of all facets, and their frequencies in the BioSamples database using a Solr query.
3. Count concurrent apperance within samples and write to a tally.
4. Process the tally and make plots with Bokeh.
5. Build a Neo4j graph as the basis of a facet reccomendation engine.
6. Build a Gephi visualisation for data exploration of the whole dataset.

## Goal

To see which facets co-occur the most. Which facets are linked and which ones rarely co-exist within a sample. This will form the basis of facet scoring mechanisms. This can be used to generate a rudimentary facet suggestion program (reccomendation engine). I'd also need to negatively score against rare facets. I will be able to use this matrix to build a graph dataset in Neo4J and a visualisation graph in Gephi. Gephi data exploration can be used to show curation needs and identify clusters of related facets. Overall we can derrive network stats to track curation improvements over time and step back to see the scope of biosamples. Ultimately we need to provide users with summerative information on the database so they know what can be found and what can't.

## Progress

### 1. Get the facets for every sample in the db. This is done using a multithreading python script Biosamples-multithreading-crawler.py.
To get the facets I used /facet_extractor.py/

### 2. Get a list of all facets, and their frequencies in the BioSamples database using a Solr query.
see /all_biosamples_characteristics.py/

This script gets the info from the API using Solr queries. I pageinate the query and go through extrancting the info. This generates a list of every facet in every sample.

I want to go through this and get the mean and mode no. of facets per sample.

### 3. Count concurrent apperance within samples and write to a tally.
see /cooccurence_matrix_generator.py/ which counts  coocurance fron the previous step. NB at first I counted the relationships with no counts but the script was extremely slow. Trying to generate a 26601 x 26601 matrix (707,613,201 possible interactions)! Instead I use dictionaries to speed it up and only count concurence > 1. We get 638282 relationships so only 0.09% of facets share a relationship. Hence the counting is much faster. We also employ multithreading. I used 8 but 10 threads worked well too. These counts are then combined with /cooccurence_matrix_combinator.py/.

### 4. Process the tally and make plots with Bokeh
I calculated OBSERVED concurrence frequency above. To calculate EXPECTED concurrence frequency:

Expected probability = ((facet1 count / total samples)*(facet2 count / total samples))

EXPECTED concurrence frequency = (Expected probability * total samples)
total samples taken as 4,698254

Difference = (OBSERVED concurrence frequency - EXPECTED concurrence frequency)

see /4analysis.py/


I have plotted the difference for each pair. This worked but ultimately with this many points (638,282) it is too slow. I worked hard to have hover over info so you can see which points correspond to which circle but it crashes on complex regions. To avoid this use the zoom tool. Unfortunately the HTML is too big to upload to github so see https://drive.google.com/open?id=0B_Bo2nc_oa_-dGZ5UEVwalN2clE

The general trends are that the data is exponential and we see a nice flat line in the middle. In that flat line most values are positive which shows general meaning to links generally and not as many negative relationships. In that flatline we still have some good info to work with. it looks flat because of the exponential plotting. latitude and longituge are very highly correlated. I'm happy this came out near the top as it shows that it worked. This plotting is not good for exploration because it is too slow. hence the need for Neo4j

I did try to build a javascript version using a highgraphs wrapper but it was just as slow. Bokeh can just convert its backend to javascript easily enough anyway.

See 2plotting.py

### 5. Build a Neo4j graph as the basis of a facet reccomendation engine.

Loading the CSV data goes somthing like this:

//Build nodes from csv

LOAD CSV WITH HEADERS FROM 'file:///cocoa_facets.csv' AS row
CREATE (:Facet {
          name:row.facets_name,
          frequency:toInteger(row.facets_count)})



//loading directional relationships (they have to be directional)
//I loaded my observed data this way
‘’’
USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM 'file:///concat_sorted_out.csv' AS row
MATCH (facet1:Facet{ name: row.Key_1}),(facet2:Facet { name: row.Key_2})
CREATE (facet1)-[:OBSERVED { frequency: row.Observed_Frequency }]->(facet2)
‘’’

Currently I'm evaluating this.

### 6. Build a Gephi visualisation for data exploration of the whole dataset.

Neo4J is not good for visualising data especially at the scale of our whole dataset. Cytoscape crashes when trying to load the data. Gephi also struggles with raw csv but if we use python to make a graph file for gephi we can then open it smoothly.

Download Gephi from https://gephi.org

Use network_plot.py to create a .gexf file for Gephi. This script can also make cytoscape graphs if required. NB I used /obs_dev_exp.py/ to make my out.csv. Thsi scrip devides observed by expected concurrence becuase a ratio results in better weighting than the subtraction. /df_sorter/ can be used to sort the dataframe by this column so you can more easily spot trends in the text file.

#### A note on Gephi.

When you load this into Gephi you must first insist that the 'Fold_Difference' or 'Difference' column becomes the edge weight. This can be done in the Data Laboratory with the 'Copy Data to Other Column' button intuitively. I also add these values to the label column so that I can see the values if I request them in the graph.

I suggest starting by changing the size of the node to be equivelent to 'Degree' aka how many edges that facet has. I followed this method https://stackoverflow.com/questions/36239873/change-node-size-gephi-0-9-1

For general help see this:
https://gephi.org/tutorials/gephi-tutorial-visualization.pdf

The next step is the layout. There are three relevent algorithms for expanding the nodes. Here are my observations on each, WARNING this is very reductive:

##### YifanHu(Proportional)
Seems the most intuitive so you can work out why things appear where they do. this is because the whole thing is a minimisation calculation based on the weights. Thats why its a circle, why big stuff tends to stay in the middle and the weakest linked stuff floats to the outer asteroid belt of junk. I reccomend starting with this because you can undertand what it is doing but it is not the best for getting discreet clusters.
##### OpenOrd
This does not give an intuitive result but it does make nice clusters for various reasons. It is supposedly the quickest but all these three work well enough with the dataset we have. It is great to watch it going through the various stages and would be perfect for a live demo.
##### ForceAtlas(2)
Default settings are nice and gives you somthing inbetween the two above. I changed a few parameters to get the largest nodes out the the edge of the screen so I could focus on smaller clusters in the middle. To do this switch on LinLog mode.

Happy visualising.



