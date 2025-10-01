##################
protege-hpo-plugin
##################


HPO Protege Plugin, based on Protege-obo-plugin.


Installation
~~~~~~~~~~~~
build the plugin with this command. ::

    $ mvn clean package

Copy the plugin to the Protege plugin directory. On my machine, this
looks like this. ::

    $ cp target/obo-annotations-plugin-0.0.2.jar ../../bin/Protege-5.2.0/plugins/.


Start Protege. The first time it starts after you copy the plugin, it will
say that it will install thje plugin and you will need to restart Protege.

You should now be able to access the Plugin at

**Window|Views|OBO Views|HPO Annotation

