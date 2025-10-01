# ldconstructor

Python module for extracting JSON fragments from graph databases.

## Example

given some RDF:

```turtle
@prefix : <http://x.org/> .

## Fred
:fred a :Person ;
      :knows :shuggy ;
      :likes :Cheese .

:shuggy a :Person ;
      :likes :Punk ;
      :livesIn :wormit .
```

We can write a program for querying this; first declare some URIs for individuals and properties:

```python
fred = 'http://x.org/fred'
knows = 'http://x.org/knows'
likes = 'http://x.org/likes'
livesIn = 'http://x.org/livesIn'
```

use rdflib to fetch a graph:

```python
    g = rdflib.Graph()
    g.parse('tests/resources/mini.ttl', format='turtle')
```

We can then construct a structure builder object:

```python
   sb = startFrom(fred,
                   knows=follow(knows,
                                livesIn=follow(livesIn)),
                   likes=follow(likes),
                   livesIn=follow(livesIn)
    )
    sb.crawler = RdflibCrawler(graph=g)
```

then use it to fetch data:

```python
    obj = sb.make()

    for person in obj.knows:
        print("Fred knows: {}".format(person))
        for town in person.livesIn:
           print("This person lives in: {}".format(town))
        
```

See tests folder for examples
