mquestioniser
#############
Medical Questionnaire Ontology Questioniser

This is a java framework that will use the terms of the MQO to create questionnaires and dynamically convert the answers to the questionnaires into a data structure with ontology terms and other features that can be computed over.

Questionnaire templates
~~~~~~~~~~~~~~~~~~~~~~~
One way of using the MQO will be to use templates to instantiate a specific questionnaire. An example template is
to be found in ``mquestionnaire-core/src/test/resources/questionnaire/example.json``.

To run the program, download or clone the current version of the Medical Questionnaire Ontology (MQO) at
its GitHub repository. Note the path of this document and of ``example.json`` and adjust the following command accordingly.

Running the demo program
~~~~~~~~~~~~~~~~~~~~~~~~
Clone this repository and run the following commands. ::

    $ mvn package
    $ java -jar mquestioniser-core/target/mquestioniser.jar questionnaire -m </path/mq-edit.owl> -q </path/example.json>

The program will produce outputs like this: ::

    Do you drink alcohol?
	    1] Never consumed alcohol
	    2] Does not currently consume alcohol
	    3] Currently consumes alcohol
    Your answer: 1
    Skipping question MQ:0010015
    ### Your reponses ###
    Alcohol consumption: Never consumed alcohol

and ::

    Do you drink alcohol?
	    1] Never consumed alcohol
	    2] Does not currently consume alcohol
	    3] Currently consumes alcohol
    Your answer: 3
    How often on average, have you had 1 glass, bottle, or can of [alcoholic beverage] beer in the past year?
	    1] 1 drink per day
	    2] 5-6 drinks per day
	    3] 2-4 drinks per day
	    4] 4-5 drinks per day
	    5] 2-3 drinks per day
	    6] 1 drink per day
	    7] Less than one drink per month
	    8] 1-3 drinks per month
	    9] 6+ drinks per day
    Your answer: 9
    ### Your reponses ###
    Alcohol consumption: Currently consumes alcohol
    Amount of alcohol consumption: 6+ drinks per day

Next up on the todo list is to implement this in the GUI.