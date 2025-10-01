# bbop-manager-sparql

## Overview

Manager for handling communication and callbacks with a SPARQL
endpoint; also allows for use of templates.

### Availability

[GitHub](https://github.com/berkeleybop/bbop-manager-sparql)

[NPM](https://www.npmjs.com/package/bbop-manager-sparql)

## API

[index](https://berkeleybop.github.io/bbop-manager-sparql/doc/index.html)

## Details

### Contributors:

Seth Carbon
Hirokazu Chiba

### Lead Contact:

Seth Carbon

### Problem:

In our survey, most abstracted JavaScript communications libraries either target a specific platform (e.g. Node.js or jQuery) or a specific framework (e.g Vue.js). The purpose of this project is to create a simple and flexible set of JavaScript communication libraries for cross-platform and cross-framework use, specifically targeted at interacting with SPARQL endpoints: bbop-manager-sparql.

### Significance

Without the creation of low-level common infrastructure, developers are left to recreate the wheel, wasting unnecessary bandwidth, and possibly creating incompatible solutions that may cause more issues down the road.

### Approach

The JavaScript library set that we will base our work on is one already in use by applications such as AmiGO and various Noctua clients, both in browsers and on the server; the BBOP libraries ( bbop-rest-manager and berkeleybop/bbop-rest-response ) are a client/server safe abstraction that has many implementation engines for both sync and async communication, across jQuery (browser), Node.js, and Rhino. In order to support the use cases we have for these libraries (automatic GET/POST switching to help endpoint caching, SPARQL templating, etc.) we first needed make adjustments and improve these core libraries before moving on to library creation. These upstream changes, bugfixes, and test coverage ended up taking the bulk of the effort; however, with these new pieces in place, progress on bbop-manager-sparql proceeded quickly. The templating use case was easily covered, but raised questions about the best approach to take in this space, where there is no apparent leading standard.

### Next steps

Moving forward, the library will develop along with the use cases of the userbase; the resolution SPARQL template handling in a standard way is already under discussion, exploring both supporting a TBD standard or multiple contenders, including the custom one already in use in the library.

### Context:

* BH17-specific workspace: https://github.com/dbcls/bh17/wiki/JavaScript-SPARQL-Libraries-(BBOP) 
* Code repository and issue tracker: https://github.com/berkeleybop/bbop-manager-sparql 
* Package repository: https://www.npmjs.com/package/bbop-manager-sparql 
* License: BSD 3-clause
