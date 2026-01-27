# Recent updates:
## 02-10-2017:
- Editing the example calls to use https instead of http calls to OLS.

## 16-05-2017
  - Adding a new function to overwrite - getGraphDataset() - and a new example to demonstrate the evil things you can do with this functionality

## 09-01-2017
  - Renaming of the physics button text
  - Getting rid of a small bug that lead to an error msg be printed if the search was used but no 'informationWindow' was present  
  - Adding the parameter 'maximumNodesPerWebserviceCall' which prints a message to the screen if the number of results are equal/bigger than the parameter. This is done to inform the user about missing data (There is a maximum number of nodes that the webservice returns)

## 19-09-2016
  - Adding the possibility to use the unclusterANode from outside (this function enables you to un-cluster one single node)
  - updates to the readme file

## 24-08-2016
  - Adding the possibility to overwrite the onclick event
  - Update of the readme file
## 08-06-2016
  - Printing error message by default to the screen if data loading fails
  - Better handling of the loading picture
  - Publishing on npm to keep git and npm in sync

## 24-05-2016
  - Minor Bug fixes for npm dependencies
  - Adjust the URL to the new OLS URL (getting rid of the beta)
  - Fixing bug when option is set to 'initialLoadingPicture: false'

## 29-04-2016
  - Added some smaller options to the visualisation to make it more flexible (Flags: *showPermaLinkBox*, *nodeShowLabel*, *nodeShowShortId*) as well as smaller internal changes
  - Added possibility of changing the hierarchical options independently of the rest (Flag: *hierarchicalLayoutVisOptions*)
  - Added possibility to have a loading picture during start up of the network (Flag: *loadingBar*)
  - Updated Readme File

# Introduction to OLS-graphview
The purpose of this plugin is to visualize ontologies, it is part of the new version of Ontology Lookup Service (OLS), provided by the EBI (European Bioinformatics Institute), that can be found at http://www.ebi.ac.uk/ols/beta. Pick an ontology, select a term in the tree view, then find the button "visualisation" (<a href="http://www.ebi.ac.uk/ols/beta/ontologies/go/terms/graph?iri=http://purl.obolibrary.org/obo/GO_0005576">Shortcut</a>). The plugin is interactive and was designed customizable to promote reusability. The reusability is demonstrated by the fact, that the the plugin is now also used by EBI's <a href='http://www.ebi.ac.uk/biosamples/'>Biosamples Database</a> to visualize Sample and group relationships (instead of ontology terms).


# How to use the plugin - user perspective
Please check the visualisation on the OLS page (see introduction). All buttons have tooltips, so it should be possible to explore the functionality quite easily with some patience. In addition, you can check the user help page, that also explains all functionality in detail. It can be found <a href="http://www.ebi.ac.uk/ols/docs/graphview-help">here</a>. I refuse to copy and paste the text and make this readme file even longer - so go there to check it out please.


# How to install the plugin - developer perspective
There are multiple ways to install the plugin:
  - Download the javascript file (ols-graphview.js) stored in the 'build' folder. Include the file by using normal script tags. See the example html pages for more information   
  - The plugin in is available as npm module - search for ols-graphview or use <a href="https://www.npmjs.com/package/ols-graphview">this link</a>
  - The widget is listed on the <a href="http://www.biojs.io">bio.js website</a> where you could find other interesting visualisation for biological data

# How to start to plugin
**PLEASE MAKE SURE YOU USE HTTPS INSTEAD OF HTTP URLS IN THE FUTURE FOR EBI WEBSERVICE CALLS**

```
var app = require("ols-graphview");
var instance = new app();
instance.visstart("ontology_vis", term, networkOptions,{});
```

The Plugin has to be started with 4 parameters: "div-id", "term",  "networkoptions" and "visoptions".

- *div-id:* is the id of the div you want to display the visualisation. E.g. if your html page has a div with the id "ontology_vis" then you might want to pass this name to the plugin
- *term:* represents the term id (URI) that you want to display, e.g. for the GO term "proteinaceous extracellular matrix" the term URI http://purl.obolibrary.org/obo/GO_0005578
- *networkoptions:* This option field is the place to set options that are related to this plugin. The necessary things to set are the options for the webservice consisting of the webservice URL and the flag for the OLS data structure, e.g. networkOptions={ webservice : {URL: "http://www.ebi.ac.uk/ols/beta/api/ontologies/go/terms?iri=", OLSschema:true}}. All other potential options are described below.
- *visoptions:* The "visoptions" are the options that the visjs library offers to the user. Almost all options can be used and overwritten. However, some of the options are overwritten during plugin execution (Mainly options for the root nodes), they can be adjusted within the other option field (“network options”). If the visoption field is empty like in the example above (visoption={}), then the plugin is started with the default options.


**NOTE: The easiest way to get the plugin up and running is to connect it to EBI's OLS webservice. Check example 1 for more information. It is possible to use your own backend - however a certain structure is expected. So if you want to use your own backend, please read the paragraph OLS - JSON structure**



# DEFAULT OPTIONS that the Plugin uses
## Default options for the network

```
var visNetworkOptions = {
 physics:{
   barnesHut: {
     gravitationalConstant: -2000,
     centralGravity: 0.3,
     springLength: 95,
     springConstant: 0.04,
     avoidOverlap: 0,
     damping: 0.09
   },
   stabilization:  {
         enabled:true,
         iterations:250,
         updateInterval:25}
 },
 interaction:{hover:true, navigationButtons:true, keyboard: false},
 layout : { hierarchical: {  enabled:false} },
 nodes:{
   shape: "box",
   mass: 2
 },
 edges : {
   scaling:{label:{
     min:12,
     max:30,
     maxVisible:30,
     drawThreshold: 12
   }},
   hoverWidth: 2,
   width : 1.5,
   selectionWidth: 2,
   shadow:true,
   font: {align:"middle"},
   arrows: "to"
 }
};
```


## Default visjs options
These are the default visjs options that are used at the moment. However, you could try to start it with many other visjs options! All visjs network Options can be found here http://visjs.org/docs/network/ (but remember, some options are overwritten within the plugin! That is what we have the second option object - network options - for!):


```
var networkOptions = {
  webservice : {URL: "no address passed", OLSschema: true},
  displayOptions : {
    showButtonBox: true,
    showInfoWindow: true,
    showLegend: true,
    showListOfExtendedNodes: true,
    showPermaLinkBox:true
  },
  dataOptions :{
    showAllRelationships: false
  },
  clusterOptions: {
    automaticClusterThreshold:50,
    parentClusterSymbole:"star",
    childrenClusterSymbole:"triangle",
    otherClusterSymbole:"dot",
    clusterMass:1,
    clusterMaxAppearanceSize: 50,
    clusterEdgeProperties:{physics:false, dashes:true, shadow:false}
  },
  appearance: {
    colorMap: ['#8dd3c7','#ffffb3','#bebada','#fba399','#80b1d3','#fdb462','#b3de69','#fccde5','#d9d9d9','#bc80bd','#ccebc5','#ffed6f',
      '#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99', "#e31a1c", '#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928',
      "#00FFFF", "#D9DCC6", "#FF7F50", "#6495ED", "#008B8B","#FF8C00","#FF1493", "#696969", "#FFD700", "#4B0082", "#808000", "#CD853F", "#B0E0E6", "#D8BFD8",
      "#00FFFF", "#D9DCC6", "#FF7F50", "#6495ED", "#008B8B","#FF8C00","#FF1493", "#696969", "#FFD700"],
    maxLabelLength: 35,
    nodeShowLabel:true,
    nodeShowShortId:true
  },
  loadingBar :{
    pictureURL: "../css/img/loading.gif",
    initialLoadingPicture: true
  },
  hierarchicalLayoutVisOptions:{
    physics:  {   hierarchicalRepulsion:{nodeDistance:200}  },
    layout:   {   hierarchical: {direction:"DU", sortMethod:"directed"}}

  },
  rootNode:{
    font:{size:14},
    color:{
      border: '#000000',
      background: '#e06868',
      highlight: {
        border: '#000000',
        background: '#e06868'},
      hover: {
        border: '#000000',
        background: '#e06868'    }
    },
    rootMass:2,
    connectingEdges:{
      color : "#e06868",
      width : 2.5
    }
  },
  collapsedRootNode:{
    font:{size:8},
    color:{
      border:'#FFAA00',
      background: '#e06868',
      highlight:{border:'#FFAA00', 	background: '#e06868',},
      hover: {border: '#FFAA00', 	background: '#e06868',}
      }
  },

  ZoomOptions:{
    scale: 1.8,
    offset: {x:0,y:0},
    animation: {
      duration: 1000,
      easingFunction: "easeInOutQuad" }
  },

  callbacks: {
    onSelectNode: onSelectNode,
    onDoubleClick: onDoubleClick,
    onSelectEdge: onSelectEdge,
    onClick: onClick
  }
};
```

## Customizing the options
*Please check the examples* to understand how to use your own options and how to overwrite the default options with your own options. Each example contains text that further explains what the example is supposed to show and tries to accomplish.  

# OLS - JSON structure:
If the option OLS structure true is activated, the plugin expects a structure similar to the OLS REST API. This means that a first webservice call (e.g.;
<a href="https://www.ebi.ac.uk/ols/beta/api/ontologies/cmpo/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_33839">here</a> ) leads to a json which includes a link to the graph data. A second webservice call actually gets the graph data as json (e.g.: <a href="https://www.ebi.ac.uk/ols/beta/api/ontologies/cmpo/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FCHEBI_33839/graph">here</a> ). To fetch data from other sources with a different structure is possible - check example 3. In this case the first webservice call is obmitted. However the plugin expects the same names/structure within the json response as demonstrated in the *second* webservice call: It is necessary to have a nodes and edges object. Nodes have to be given an id or iri, an edge is defined by a source, a target and a label of the edge. Please check the link a couple of lines above this to see the structure!

# Contact
Please <a href="https://github.com/LLTommy/OLS-graphview">use github</a> to report **bugs**, discuss potential **new features** or **ask questions** in general.

# License
The plugin is released under the Apache License Version 2.0. You can find out more about it at http://www.apache.org/licenses/LICENSE-2.0 or within the license file of the repository.

# Dependencies
* **JQuery:** Is used by the plugin (version 1.7+) https://jquery.com and therefor has to be available

# Relying on
* **visjs:** The plugin uses visjs as mention multiple times. The library has a lot more to offer than 'just' network graphs, so if you are interested, check it out at http://visjs.org. Since visjs is packed into the build/ols-graphview.js, you do not have to include it externally.
* **awesomeplete:** Is used as a autocomplete js library for the searchbox (https://leaverou.github.io/awesomplete/). Awesomeplete is packed into the build/ols-graphview.js, you do not have to include it externally.

# If you are interested in this plugin...
...you might also want to have a look at the *ols-treeview* package as well, see <a href="https://github.com/LLTommy/OLS-treeview">Github</a> or <a href="https://www.npmjs.com/package/ols-treeview">npm</a>
