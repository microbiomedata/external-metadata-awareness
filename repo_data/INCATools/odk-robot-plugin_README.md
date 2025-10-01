ODK ROBOT plugin
================

This is a [ROBOT](http://robot.obolibrary.org/) plugin intended to be
used within the [Ontology Development
Kit](https://github.com/INCATools/ontology-development-kit) (ODK). It
provides additional ROBOT commands to perform tasks not covered by the
ROBOT built-in command set.

Available commands
------------------
The following commands are provided by the plugin:

* `odk:subset`: to create ontology subsets;
* `odk:check-align`: to check the alignment of an ontology against an
  upper-level ontology and/or arbitrary root terms;
* `odk:normalize`: to “normalise” an ontology,
* `odk:import`: to add/remove import declarations.

Building
--------
Build with Maven by running:

```sh
mvn clean package
```

This will produce two Jar files in the `target` directory.

The `odk.jar` file is the plugin itself. Place this file in your ROBOT
plugins directory (by default `~/.robot/plugins`), then call the
commands by prefixing them with the basename of the Jar file in the
plugins directory.

For example, if you placed the plugin at `~/.robot/plugins/odk.jar`,
you may call the `subset` command as follows:

```sh
robot odk:subset ...
```

The `odk-robot-standalone-X.Y.Z.jar` file is a standalone version of
ROBOT that includes the commands provided by this plugin as is they were
built-in commands. It is mostly intended for testing and debugging, as
it allows using the commands from the plugin without having to actually
install the plugin in a ROBOT plugins directory.

Using with the ODK
------------------
The plugin is (or will be) provided with the ODK Docker image. To use it
as part of a ODK workflow, all that is needed is to make the rule in
which the plugin is to be used depend on the ODK built-in rule
`all_robot_plugins`. This will make the plugin available in the
repository’s `src/ontology/tmp/plugins` directory, which is already set,
in ODK workflows, as the ROBOT plugins directory.

For example:

```make
target.owl: source1.owl source2.owl | all_robot_plugins
        $(ROBOT) merge -i source1.owl -i source2.owl \
                 odk:subset --subset MY_SUBSET \
                            --output target.owl
```

The plugin can also be used outside of any ODK workflow, by manually
instructing ROBOT to look for plugins into the `/tools/robot-plugins/`
directory (e.g. by setting the `ROBOT_PLUGINS_DIRECTORY` environment
variable to that directory).

Copying
-------
The ODK ROBOT plugin is distributed under the same terms as the Ontology
Development Kit itself (3-clause BSD license). See the
[COPYING file](COPYING) in the source distribution.
