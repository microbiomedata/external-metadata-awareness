# bbop-rest-response

## Overview

Generic handler for dealing with the gross parsing and handling of
responses from a RESTful service.

In an ideal world, nobody should be probing/decoding responses from
services manually, but this happens all too often as people try and
make progress as their increasingly complicated applications
evolve--too many errors creep in as data "schema" change and people
write or use conflicting or out-of-date probulators.

The generic BBOP RESTful response is a class that can be instantiated
with either a a string or a JSON object and specifies the following functions:

* raw (the initial input)
* okay (whether the input is properly structured or otherwise "correct")
* message (something that wants to be communicated about the instantiation)
* message_type (the type of message to be communicated)

The pattern presented here is intended to be subclassed to create useful and rich types for understanding the responses for your various and sundry data services. More specifically, this is intended to be used with the automatic response  instantiation of [bbop-rest-manager](https://github.com/berkeleybop/bbop-rest-manager)s.

This package contains a "null" and a simple JSON version of this
functionality. For more detailed information, please see
the [unit tests](https://github.com/berkeleybop/bbop-rest-response/tree/master/tests).

## Availability

[GitHub](https://github.com/berkeleybop/bbop-rest-response)

[NPM](https://www.npmjs.com/package/bbop-rest-response)

## API

[index](https://berkeleybop.github.io/bbop-rest-response/doc/index.html)
