# bbop-rest-manager

## Overview

The purpose of the bbop-rest-manager is simple: to create an
easy-to-use JavaScript abstraction for getting external data, usually
from REST resource, that allows code reuse across client, server, and
different response systems (promises, function callbacks, jQuery AJAX,
or asynchronous or synchronous Node.js server).

All it needs to function is a RESTful resource to contact and a
compliant response class (see
superclass
[bbop-rest-response](https://github.com/berkeleybop/bbop-rest-response). With
this and a single change in a single line in your code, you can run it
on the server in Node, on a web client, or as a script.

(With a small amount of work, we could make this autodetect as well so
no changes would be needed; we could also port this to Rhino or
PurpleJS.)

For solid examples of what this does, please see
the
[unit tests](https://github.com/berkeleybop/bbop-rest-manager/tree/master/tests),
starting with core.tests.js.

This is the "new" base (superclass) version of the manager for BBOP
systems.

## Availability

[GitHub](https://github.com/berkeleybop/bbop-rest-manager)

[NPM](https://www.npmjs.com/package/bbop-rest-manager)

## API

[index](https://berkeleybop.github.io/bbop-rest-manager/doc/index.html)
