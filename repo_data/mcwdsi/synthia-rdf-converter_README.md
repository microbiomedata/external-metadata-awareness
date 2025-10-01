## Setup
First you need to install [SBT](http://www.scala-sbt.org/).  SBT will install the other dependencies.

Also, you'll need to extract the synthetic population files generated from PUMS data.  You'll find these in the `src/main/resources` folder.  Extract using tar.

## To Run
Once you've got your dependencies set up (installed SBT and extracted the files), use SBT to generate the OWL files using the `sbt run` command.

You'll need a significant amount of memory for Miami-Dade county.  To adjust the Java heap size with SBT, use the `-J-Xmx##G` switch for SBT where the `##` is the number of GB to set the max heap size, varying the memory as needed.  The final command would look something like `sbt -J-Xmx12G run`

By default, the script will create the Alachua County owl file.  To create the Miami-Dade County owl file, you'll need to modify the script.  Find the following line of code in the `src/main/scala/Main.scala` file:

    val fileStem = "/2010_ver1_12001_"  //change to "/2010_ver1_42003_" to process Miami-Dade county instead of Alachua County

Change it to look like the following:

    val fileStem = "/2010_ver1_42003_" //after change to process Miami-Dade County

Run the program in the same way as before: `sbt -J-Xmx12G run`