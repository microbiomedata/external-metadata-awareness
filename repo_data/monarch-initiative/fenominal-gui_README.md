# fenominal-gui
Graphical User Interface for Fenominal


## Building fenominal-gui

While we are in the process of adding fenominal to maven central, building the GUI requires a local 
maven install of fenominal (the version in the pom file must match the locally install version of
fenominal).

```bazaar
git clone https://github.com/monarch-initiative/fenominal.git
cd fenominal
mvn install
```
We also need to locally install phenopacket-tools v0.4.0.
```bazaar
https://github.com/phenopackets/phenopacket-tools.git
cd phenopacket-tools
git checkout v0.4.0
mvn clean install
```

## Running GUI app

Assuming the build completed successfully, the GUI is run by the following command:

```bash
java -jar fenominal-gui/target/fenominal-gui-${project.version}.jar
```

Please refer to the documentation to learn more about various GUI features.

## Making this a modular app

Currently there seems to be no way around this issue
class org.controlsfx.control.textfield.AutoCompletionBinding (in module org.controlsfx.controls) cannot access class com.sun.javafx.event.EventHandlerManager (in module javafx.base) because module javafx.base does not export com.sun.javafx.event to module org.controlsfx.controls
class org.controlsfx.control.textfield.AutoCompletionBinding (in module org.controlsfx.controls) cannot access class com.sun.javafx.event.EventHandlerManager (in module javafx.base) because module javafx.base does not export com.sun.javafx.event to module org.controlsfx.controls
at org.controlsfx.controls/org.controlsfx.control.textfield.AutoCompletionBinding.<init>(AutoCompletionBinding.java:538)

```bazaar
module org.monarchinitiative.fenominal.gui {
    requires spring.beans;
    requires spring.context;
    requires javafx.graphics;
    requires javafx.controls;
    requires javafx.fxml;
    requires javafx.web;
    requires java.sql;
    requires org.monarchinitiative.phenol.core;
    requires org.monarchinitiative.phenol.io;
    requires org.slf4j;
    requires org.monarchinitiative.fenominal.core;
    requires jdk.jsobject;
    requires com.google.protobuf;
    requires com.google.protobuf.util;
    requires org.phenopackets.schema;
    requires org.phenopackets.phenopackettools.builder;
    requires json.simple;
    requires spring.boot.autoconfigure;
    requires org.controlsfx.controls;
    requires spring.boot;
    requires spring.core;

    exports org.monarchinitiative.fenominal.gui to javafx.graphics, spring.beans, spring.context;
    opens org.monarchinitiative.fenominal.gui to spring.core;
    opens org.monarchinitiative.fenominal.gui.config to spring.core;
    exports org.monarchinitiative.fenominal.gui.config to spring.beans, spring.context;
    exports org.monarchinitiative.fenominal.gui.controller to spring.beans;
    opens org.monarchinitiative.fenominal.gui.controller to spring.core, javafx.fxml;
    opens org.monarchinitiative.fenominal.gui.hpotextminingwidget to javafx.fxml;
}
```

