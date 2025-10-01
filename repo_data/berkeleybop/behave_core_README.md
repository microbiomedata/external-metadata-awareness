* behave_core

  A python library of common functionality and steps for use with the
  Behave testing framework.

  The intention is to collect the common parts of testing modern
  websites and RESTful services into a single location, while leaving
  the important application-specific stuff in with their respective
  repos.

** environment

   A collection of functions to help setup the initial environment for
   behave.

** page

   A collection of steps and functions for dealing with the basic
   examination of HTML and webapp pages.

** resource

   A collection of steps and functions for dealing with acquiring data
   across the internet.

** json_data

   A collection of steps and functions for dealing with the parsing of
   JSON data.

* roadmap

  - Get this library to be the common base of:
    - geneontology/amigo
    - geneontology/go-site
    - possibly monarch
  - As this matures, we'd like to make it into a proper pip.
