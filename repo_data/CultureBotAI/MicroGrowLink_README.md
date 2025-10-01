# MicroGrowLink

MicroGrowLink is a knowledge graph–based framework for predicting microbial growth media using advanced graph and transformer models. It integrates microbial, chemical, and environmental data into a heterogeneous knowledge graph and applies link prediction to forecast which media enable growth of given taxa.

## Supported Models

- **RGT (Relational Graph Transformer)**
- **HGT (Heterogeneous Graph Transformer)**
- **NBFNet (Neural Bellman–Ford Network)**

_Relational GCNs (RGCNs) have been deprecated and are no longer maintained._

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Prepare data: place the KGX TSV files in `data/`:
   - `merged-kg_nodes.tsv`
   - `merged-kg_edges.tsv`
3. Train or predict using your chosen model:
   - See [docs/RGT.md](docs/RGT.md)
   - See [docs/HGT.md](docs/HGT.md)
   - See [docs/NBFNet.md](docs/NBFNet.md)

## Directory Structure

```
MicroGrowLink/
├── data/                    # KGX data and taxa lists
├── hpc/                     # SLURM scripts for multi‐GPU runs
├── scripts/                 # Utility scripts and local launchers
├── src/                     # Source code
│   ├── learn/               # Model implementations and prediction scripts
│   └── eval/                # Evaluation scripts
├── docs/                    # Model‐specific documentation
├── predictions/            # Output prediction files
└── README.md                # This overview
```

## Contributing

Contributions welcome! Please open issues or pull requests with clear descriptions and tests. Follow the existing code style and update documentation accordingly.
