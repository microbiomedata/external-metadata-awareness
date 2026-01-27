# ontology class rubrics

these rubrics are to provide a framework for systematically evaluating whether an individual term should be included in an ontology. 

it is designed to provide a flexible framework. not every person or ontology group will agree on how to weigh each rubric. 

it is also designed to be technically flexible. a complete schema is provided, and evaluation of a class can be encoded in json or rdf. however, it can also be used ina lightweight fashion with google sheets or excel, or as tables in a manuscript. or in fact it can be simply used as a framework for talking and discussing about terms.

## rubrics

### scope

### usage in literature

does the class correspond to a concept that has a distinct name or set of names in the literature?

### adherence to upper level concepts

different ontologies may adhere to different upper ontologies, which may be at different levels of specificity. it is up to each ontology to decide which upper ontologies, if any, to commit to. whichever choice is made, this should be clearly articulated in the ontology documentation. 

GO commits to its own subdivision into molecular function, biological process, and cellular component. many anatomy ontologies commit to a broad distinction between anatomical entities and developmental stages. in addition there may be further commitment to mid upper ontologies like caro or cob, and beyond that to philosophical ontologies like bfo.

### does it divide the world in a way that makes sense for domain scientists

this is particularly important for terms that are higher up in the class hierarchy

### utility for querying

### logical utility

does avoiding including this class result in awkward repetition of expressions?

### database coherence

### operationality: can it be populated consistently

### completeness: do you have a strategy for ensuring consistent population 

### consistency with existing terms

### balanced

### fits with existing design patterns

### single child

