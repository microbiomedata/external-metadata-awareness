#+TITLE: BBOPX JS README
#+Options: num:nil
#+STARTUP: odd
#+Style: <style> h1,h2,h3 {font-family: arial, helvetica, sans-serif} </style>

* Overview

  BBOPX JS the experimental wing of the [[http://github.com/berkeleybop/bbop-js][BBOP JS]] library.

  As this is an experimental library, although the code may be used,
  it will forever be pre-1.0.

** Usage

   BBOPX has a slightly better thought out shim, meaning that using in
   a CommonJS environment is a little easier:

  #+BEGIN_SRC javascript
var bbopx = require('bbopx');
  #+END_SRC

   As opposed to BBOP's (currently odd) form:
   
  #+BEGIN_SRC javascript
var bbop = require('bbop').bbop;
  #+END_SRC


** API
   More or less current API documentation can be found [[https://berkeleybop.github.io/bbopx-js/][here]].

* bbopx.barista.response

  For readability, the original README.org org-mode doc may well work
  better.

  This document seeks to describe the barista response. It is a work
  in progress that is evolving along with the current
  implementation. It should seek to document the ideal that we're
  working towards as well as the current implementation.
  
  There is currently no difference between the barista response and
  the more rich barista response from minerva requests. Properly, the
  latter should be a subclass of the former, and will have to be if
  this pattern is generalized out to include other services behind
  barista.
  
  The minimal response must have:
  
  - message_type
  - message

  And if there is commentary, it, as well as the message_type and
  message, must be strings.

** top-level object
*** message_type
    A simple thumbs up or thumbs down 
**** error
     The action was not successfully carried out.
**** success
     The action was successfully carried out.
*** message
     A short summary explaining the response. Think: "term added" or
     "server caught fire".
*** commentary [optional]
    A detailed commentary on the mesage and message type. Think things
    like stack traces and the like.
*** data
    This is where the "interesting" bits of a successful response should
    live. It is an object.
*** uid
    This is a pass-through from the client. It may be critical some
    places, but not others.
*** intention
    This is a pass-through from the client. It reports what the client
    wanted to accomplish with their query. In general, "query"s are
    just passed back to the requesting client, while "action"s may be
    passed back to all as items are updated.
**** query
     Answer a question that this client has.
**** action
     Perform a possibly world-changing action.
*** signal
    This is the opinion of 
**** merge
     The change to the entity is such that changes can be merged
     in. No problem; here they are.
**** rebuild
     The change to the entity is such that you will have to rebuild it
     from scratch. With this.
**** meta
     Likely the response to a "query".
     
