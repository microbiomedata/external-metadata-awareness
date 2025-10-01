[![Build Status](https://travis-ci.org/berkeleybop/bbop-response-golr.svg)](https://travis-ci.org/berkeleybop/bbop-response-golr)

# bbop-response-golr

## Overview

Response type and API for handling the responses from a GOlr instance
(Solr server with a structured schema) in a standard way.

In addition to the base functionality provided by [bbop-rest-response](https://github.com/berkeleybop/bbop-rest-response), this class adds a ton of extra functionality for checking responses and accessing different parts of the return document in a consistent way. For a (small) sample of methods:

* total\_documents, start\_document, end\_document (document counting)
* paging\_previous\_p, paging\_next\_p (paging handling)
* documents, get\_doc (general document access)
* get\_doc\_field, get\_doc\_label (document field access)
* much more...

This is a subclass of [bbop-rest-response](https://github.com/berkeleybop/bbop-rest-response). For more detailed information, please see
the [unit tests](https://github.com/berkeleybop/bbop-response-golr/tree/master/tests).

## Availability

[GitHub](https://github.com/berkeleybop/bbop-response-golr)

[NPM](https://www.npmjs.com/package/bbop-response-golr)

## API

[index](https://berkeleybop.github.io/bbop-response-golr/doc/index.html)
