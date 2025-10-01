# kg-ai-prep

Package to prep knowledge graphs for AI model training, with a focus on biomedical KGs and effective graph learning.

## Overview

kg-ai-prep addresses the challenge of preparing large, complex knowledge graphs (like KG-Microbe) for training graph embedding models. Raw knowledge graphs often contain structural and relational noise that hinders model performance, leading to issues like:

- **Embedding collapse**: embeddings converging to trivial values
- **Low-confidence predictions**: models struggling with noisy or irrelevant structure
- **Training instability**: difficulty finding stable hyperparameters

This package implements research-backed filtering strategies to create task-focused, high-quality subgraphs that improve model training and prediction performance.

## Key Features

### 🔍 **Comprehensive Graph Analysis**
- Connected component analysis with bridge/articulation point detection
- Degree distribution statistics and hub node identification  
- K-core decomposition for structural analysis
- Quality control metrics and reporting

### 🎛️ **Advanced Filtering Strategies**

**Structural Filters:**
- Singleton removal (degree = 0 nodes)
- Leaf pruning (degree = 1 nodes) with model-specific policies
- Degree-based filtering (min/max thresholds)
- K-core extraction for dense subgraphs
- Hub node detection and removal

**Component Filters:**
- Giant component extraction
- Small component removal with size thresholds
- Disconnected subgraph handling
- Bridge edge identification

**Relational Filters:**
- Task-specific relation filtering
- Redundant and inverse relation removal
- Confidence-based edge filtering
- Contradiction detection

**Metapath Filters:**
- Domain knowledge-guided subgraph extraction
- Multi-hop relationship preservation
- Task-relevant path identification

### 🎯 **Model-Specific Optimization**

**RotatE/TransE**: Remove singletons and leaves, focus on dense connectivity
**RGT/GNNs**: Preserve attribute nodes as features, k-core filtering  
**A*Net**: Ensure path connectivity, minimum degree requirements

### 📊 **Data Splitting & Export**
- Transductive and inductive splitting strategies
- Hard negative sampling with type consistency
- Export formats for RotatE, RGT, and A*Net models
- Split validation and leakage detection

## Installation

```bash
# Using uv (recommended)
git clone https://github.com/vimss/kg-ai-prep
cd kg-ai-prep
uv pip install -e ".[dev]"

# Using pip
pip install -e ".[dev]"
```

**Note**: The package uses NetworkX as fallback when GRAPE is not available (e.g., on Mac ARM systems).

## Quick Start

### Command Line Usage

```bash
# Analyze graph structure
kg-ai-prep analyze nodes.tsv edges.tsv --target-relation "microbe_grows_in_medium"

# Full preprocessing pipeline
kg-ai-prep preprocess nodes.tsv edges.tsv \
    --output-dir processed_kg/ \
    --remove-singletons \
    --min-degree 2 \
    --giant-component-only \
    --target-relation "biolink:interacts_with" \
    --export-rotate

# Generate model-specific config
kg-ai-prep generate-config rotate_config.json --model-type rotate
```

### Python API

```python
from kg_ai_prep import KGPreprocessor, FilterConfig, SplitConfig

# Initialize preprocessor
prep = KGPreprocessor()

# Load KGX format data
graph = prep.load_kgx("nodes.tsv", "edges.tsv")

# Analyze original graph
report = prep.analyze(graph)
print(f"Graph: {report.n_nodes} nodes, {report.n_edges} edges")
print(f"Components: {report.components.n_components}")
print(f"Singletons: {report.degrees.n_singletons}")

# Apply task-specific filtering
config = FilterConfig(
    target_relation="microbe_grows_in_medium",
    remove_singletons=True,
    min_degree=2,
    keep_giant_component_only=True,
    model_type="rotate"
)

filtered_graph = prep.filter(graph, config)

# Create train/val/test splits
split_config = SplitConfig(
    strategy="transductive_edge",
    ratios=(0.8, 0.1, 0.1),
    negative_sampling_ratio=1.0,
    hard_negatives=True
)

splits = prep.split(filtered_graph, split_config)

# Export for different models
prep.export_rotate(splits, "rotate_output/")
prep.export_rgt(splits, "rgt_output/") 
prep.export_astar(splits, "astar_output/")
```

## Advanced Usage

### Metapath-Based Filtering

```python
from kg_ai_prep import MetaPath

# Define metapaths connecting taxa to growth media
metapaths = [
    MetaPath(path=["biolink:OrganismTaxon", "biolink:capable_of", "biolink:MolecularActivity"]),
    MetaPath(path=["biolink:MolecularActivity", "biolink:consumes", "biolink:ChemicalEntity"]),
    MetaPath(path=["biolink:ChemicalEntity", "biolink:part_of", "biolink:EnvironmentalFeature"])
]

config = FilterConfig(
    target_relation="microbe_grows_in_medium",
    metapaths=metapaths,
    model_type="astar"
)
```

### Model-Specific Configurations

```bash
# RotatE: Focus on dense connectivity
kg-ai-prep preprocess nodes.tsv edges.tsv \
    --model-type rotate \
    --remove-singletons \
    --remove-leaves \
    --min-degree 1 \
    --export-rotate

# RGT: Preserve features and structure  
kg-ai-prep preprocess nodes.tsv edges.tsv \
    --model-type rgt \
    --remove-singletons \
    --k-core 2 \
    --compress-attributes \
    --export-rgt

# A*Net: Ensure path connectivity
kg-ai-prep preprocess nodes.tsv edges.tsv \
    --model-type astar \
    --min-degree 2 \
    --k-core 2 \
    --export-astar
```

## Filtering Strategies

### Problem Patterns Addressed

1. **Irrelevant Relations**: Edges not related to target prediction task
2. **Data Imbalance**: Target relations are rare compared to other edge types  
3. **Hub Nodes**: Very high-degree nodes that dominate training
4. **Isolated Nodes**: Singletons and leaves that provide little context
5. **Redundant Edges**: Duplicate or inverse relationships
6. **Disconnected Components**: Subgraphs not connected to main structure

### Solution Approaches

**Degree-Based Filtering:**
```bash
# Remove problematic low/high degree nodes
--remove-singletons     # Remove degree-0 nodes
--remove-leaves        # Remove degree-1 nodes (model dependent)
--min-degree 2         # Minimum degree threshold
--max-degree 1000      # Hub removal threshold
```

**Component-Based Filtering:**
```bash
# Focus on main connected structure
--giant-component-only    # Keep largest component only
--min-component-size 10   # Minimum component size
```

**Relation-Based Filtering:**
```bash
# Task-specific relation curation
--target-relation "biolink:interacts_with"
--keep-relations "biolink:regulates" "biolink:affects"
--drop-relations "biolink:same_as" "biolink:equivalent_to"
--min-edge-confidence 0.7
```

## Data Format

### Input: KGX TSV Format

**Nodes file (`nodes.tsv`):**
```tsv
id	category	name	description
CHEBI:16828	biolink:ChemicalEntity	L-tryptophan	Amino acid
EC:4.1.99.1	biolink:Enzyme	tryptophan deaminase	Enzyme
```

**Edges file (`edges.tsv`):**
```tsv
subject	predicate	object	confidence
CHEBI:16828	biolink:participates_in	EC:4.1.99.1	0.95
```

### Output Formats

**RotatE Format:**
```
train.txt, val.txt, test.txt (tab-separated triples)
entity2id.txt, relation2id.txt (vocabularies)
```

**RGT Format:**
```
train_graph.json, val_graph.json, test_graph.json
node_features.json, vocabularies.json
```

**A*Net Format:**
```
graph.json (with path costs)
val_queries.json, test_queries.json (path reasoning tasks)
```

## Development

```bash
# Setup development environment
git clone https://github.com/vimss/kg-ai-prep
cd kg-ai-prep
uv pip install -e ".[dev]"

# Run tests
just test-basic          # Basic functionality test
just test               # Full test suite  
just test-cov           # With coverage

# Code quality
just lint               # Ruff linting
just format             # Code formatting
just typecheck          # MyPy type checking

# Create test data
just create-test-data   # Generate small subgraph for development

# Test CLI
just test-cli           # Test command line interface
just test-pipeline      # Full pipeline test
```

## Performance Benefits

Based on research by Ratajczak et al. (2022), proper KG filtering can:

- **Improve model performance by 20-40%** on target prediction tasks
- **Reduce training time and memory usage** by removing 26-60% of irrelevant nodes
- **Increase prediction confidence** by eliminating structural noise
- **Enable more stable hyperparameter tuning** with cleaner data

## Research Background

This package implements filtering strategies from:

> "Filtering Knowledge Graphs for Better Biomedical Graph Learning" (Ratajczak et al., 2022)

Key insights:
- Task-focused filtering dramatically improves link prediction
- Removing counterproductive structure is better than adding more data
- Model-specific filtering policies optimize for different architectures
- Metapath-guided extraction preserves domain knowledge

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with tests
4. Run quality checks (`just check`)
5. Submit pull request

## License

MIT License - see [LICENSE](LICENSE) file.

## Citation

If you use kg-ai-prep in your research, please cite:

```bibtex
@software{kg_ai_prep,
  title = {kg-ai-prep: Package to prep KGs for AI model training},
  author = {VIMSS Ontology Team},
  url = {https://github.com/vimss/kg-ai-prep},
  year = {2024}
}
```

## Support

- **Issues**: [GitHub Issues](https://github.com/vimss/kg-ai-prep/issues)
- **Documentation**: [Full docs](https://vimss.github.io/kg-ai-prep)
- **Discussions**: [GitHub Discussions](https://github.com/vimss/kg-ai-prep/discussions)
