# biolink graphviz demo

Adapted from: https://github.com/DoctorBud/graphviz-viewer

This lightweight web application is intended to be deployed as a static single-page website, for demoing an app that combines

 * simple biolink-api calls
 * use of obographviz library
 * visualization using Viz

## Screenshot

![img](images/screenshot.png)

## Usage

## Requirements to build

This is what I use, you may get lucky with slightly older/newer versions.

- NodeJS 4.5.0
- NPM 3.10.8



## Requirements to run

Tested on MacOSX Safari, Chrome and FireFox. Requires some form of http-server. `npm run dev` will invoke the WebPack server for auto-bundling during development, and this is sufficient for demo purposes.


## Building

```
cd graphviz-viewer/ # If you aren't alread there
npm install
npm run build    # 'npm run fastbuild' to avoid minification
```

## Running

```
npm run dev
open http://localhost:8080/webpack-dev-server/graphviz-viewer # On MacOSX
# Alternatively, point your browser to:
#   http://localhost:8080/webpack-dev-server/graphviz-viewer
#
```
