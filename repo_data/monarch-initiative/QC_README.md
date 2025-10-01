## Monarch QC Vuepress site

### About

Monarch generates a number of QC and documentation artifacts each release including:
1. [Solr pivot tables](https://qc.monarchinitiative.org/solr/) ({source, taxa} x {association, relation}) as markdown
2. [Namespace, relation, namespace graphs](https://qc.monarchinitiative.org/dipper/) as graphviz and markdown tables
3. [SciGraph category diffs](https://qc.monarchinitiative.org/scigraph.html) as markdown
4. [Monarch rule violations](https://qc.monarchinitiative.org/rules/) as markdown
5. [Biolink schemas](https://qc.monarchinitiative.org/biolink/schema.html) as graphviz

This vuepress app is built by slurping up these various resources documents
and displaying them in a centralized dashboard, which also includes [plotly
heatmaps](https://qc.monarchinitiative.org/) of solr pivot tables.

The app runs off of github pages and is hosted on https://qc.monarchinitiative.org/


### Building the app

A makefile is included to download the various files:

```
make
```

To run the vuepress app locally


VuePress requires Node.js >= 8.6:

With yarn:
```bash
yarn dev
```

Or with npm
```bash
npm install
npm run dev
```

To build the docs directory for production
```bash
yarn build
```
or
```bash
npm run build
```

To deploy to github pages (builds docs directory and pushes to github):
```bash
./deploy.sh
```


For more details on vuepress, please head VuePress's [documentation](https://v1.vuepress.vuejs.org/).
