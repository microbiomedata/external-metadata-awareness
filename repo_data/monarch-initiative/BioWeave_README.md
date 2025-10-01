# bioweave

BioWeave prototype

## Requirements to build

This is what I use, you may get lucky with slightly older/newer versions.

- NodeJS 4.5.0
- NPM 3.10.8

```

## Requirements to run

Tested on MacOSX Safari, Chrome and FireFox. Requires some form of http-server. `npm run dev` will invoke the WebPack server for auto-bundling during development, and this is sufficient for demo purposes.


## Building

```
cd bioweave/ # If you aren't already there
npm install
npm run build
http-server -c-1 docs/     # Run an http-server with caching off and content in docs/
open http://127.0.0.1:8080 # On MacOSX
# Alternatively, point your browser to:
#   http://127.0.0.1:8080
#
```

## Running in Development Mode

```
npm run dev
open http://localhost:8080/webpack-dev-server/ # On MacOSX
# Alternatively, point your browser to:
#   http://localhost:8080/webpack-dev-server/
#
```
