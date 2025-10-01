# Behavior Lego

Example:

![Figure](https://raw.github.com/cmungall/behavior-lego/master/screenshots/impala.png)

 * Blue boxes indicate an instance of a behavioral unit
 * White box on top of blue box indicates the agent driving the behavior
 * Yello box to side indicates where the behavior happens. For multi-organism this is an ENVO term. For single-organism it is an anatomical location.

This toy example shows a lion chasing an impala in the savanna, biting
a chunk of flesh, swallowing, digesting and then defecating in a
hedge (I couldn't find an ENVO term for the den of a lion).

There is a bit of weirdness due to the lack of digestion process in
NBO.

## Requirements:

 * Protege 4
 * GO LEGO plugin - http://wiki.geneontology.org/index.php/Ontology_editor_plugins

## Setting up

Installs:

 * Install Protege (4.2) -- http://protege.stanford.edu
 * Install Elk (0.3 or higher) -- http://code.google.com/p/elk-reasoner/downloads/list
 * Install lego plugin --  http://code.google.com/p/owltools/downloads/list

In Protege menu, select:

 * Views / Ontology Views / Lego annotations

  (I place this in my Individuals tab)

Or you can instead use a tab:

 * Tabs/Lego annotations


Getting started
---------------

  cp template.owl my-ethogram.owl

open my-ethogram.owl in Protege4

Note:

You can configure imports how you like. Current the default is

 * envo
 * nbo (for the behavir units)
 * go (for other processes)
 * uberon (for anatomy)

You will be spending most of your time in the "Individuals tab"

General tip: work backwards. If you create the node at the end of the
arrow it will "be there waiting for you" when you create the source
node. Ultimately it's up to you.

Click the "+<>" in the top left. Give the behavior unit a
name. E.g. "lion chasing impala".  The label isn't visible in the lego
tab but it will help you organize.

Under "Types" add (+):

* A class from BFO (e.g. "feeding behavior")
* A class expression "enabled_by some <Anatomical Structure>"
* A class expression "occurs_in some <Envo or Anatomical Structure>"

Under "property assertions" add:

* precedes <activity>
* part_of <grouping process>

You might want to make the process individual first

You can use other behavior ontologies than ENVO but there is a hack
you have to do first. Make the root a child of
molecular_function. This is temporary until we make the LEGO plugin
more configurable.


