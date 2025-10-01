# Fitness MCP - Agrobacterium Mutant Analysis

A FastMCP server for analyzing fitness data from barcoded Agrobacterium mutant libraries grown in mixed cultures across different conditions.

## Overview

This MCP provides tools to analyze gene fitness data from transposon insertion mutant libraries. Each row in the dataset represents a gene knockout mutant, and the fitness scores indicate how well that mutant thrives compared to the wild-type strain under specific growth conditions.

### Understanding Fitness Scores

**Critical**: Fitness scores use the following interpretation:
- **Negative values**: Gene knockout **improves** fitness → The gene normally **inhibits growth** in this condition
- **Positive values**: Gene knockout **reduces** fitness → The gene is **beneficial/essential** for growth in this condition  
- **Values near 0**: Gene knockout has **minimal effect** on fitness in this condition

## Data Files

- `data/fit_t.tab`: Main fitness data (90MB TSV)
  - Columns 1-3: Gene metadata (locusId, sysName, description)
  - Remaining columns: Fitness scores for each experimental condition
- `data/exp_organism_Agro.txt`: Experimental condition descriptions
  - Detailed metadata for each growth condition including media, temperature, pH, treatments

## Available MCP Tools

### Basic Gene Information
- `get_gene_info(gene_id)`: Get basic gene metadata
- `search_genes(query, limit)`: Search genes by name or description

### Fitness Analysis  
- `get_gene_fitness(gene_id, condition_filter)`: Get fitness scores across conditions
- `analyze_gene_fitness(gene_id, min_fitness, max_fitness)`: Categorize fitness effects
- `interpret_fitness_score(fitness_score)`: Get biological interpretation of a score

### Condition Information
- `get_growth_conditions(condition_filter)`: List available conditions
- `get_condition_details(condition_name)`: Get detailed experimental metadata

### Discovery Tools
- `find_essential_genes(condition_filter, min_fitness_threshold, limit)`: Find genes that appear essential (positive fitness scores)
- `find_growth_inhibitor_genes(condition_filter, max_fitness_threshold, limit)`: Find genes that inhibit growth (negative fitness scores)

## Example Usage

```python
# Find genes essential for growth in pH conditions
essential_in_ph = find_essential_genes(condition_filter="pH", min_fitness_threshold=0.5)

# Find genes that inhibit growth in carbon source conditions  
growth_inhibitors = find_growth_inhibitor_genes(condition_filter="carbon", max_fitness_threshold=-0.5)

# Analyze a specific gene's fitness profile
gene_analysis = analyze_gene_fitness("Atu0001")

# Get details about a specific experimental condition
condition_info = get_condition_details("set10IT020")  # R2A pH 5.5
```

## Biological Context

This dataset comes from high-throughput fitness experiments using:
- **Organism**: *Agrobacterium tumefaciens* 
- **Method**: Barcoded transposon insertion mutant library
- **Measurement**: Competitive fitness in mixed culture
- **Conditions**: Various carbon sources, pH levels, stress conditions, etc.

The fitness scores represent the log2 ratio of mutant abundance after vs. before growth, normalized to controls. This allows identification of:
- **Essential genes**: Required for growth under specific conditions
- **Growth inhibitors**: Genes that limit growth when active
- **Condition-specific gene functions**: How gene importance varies across environments

## Installation

Install the package with uv:

```bash
uv sync --dev
```

## Usage

You can run the MCP:

```bash
uv run fitness-mcp
```

Or install globally and run:

```bash
uvx fitness-mcp
```

Or import in your Python code:

```python
from fitness_mcp.main import mcp

mcp.run()
```

## Architecture

The MCP follows best practices for handling large TSV files:
- **Single data load**: 90MB TSV loaded once and shared across all tools
- **Thread safety**: Concurrent tool calls handled safely with locks
- **File monitoring**: Automatically reloads if data files change
- **Caching**: LRU caches for expensive search/filter operations
- **Efficient memory**: Optimized data structures for fast gene lookups

## Data Sources

Fitness data generated using protocols similar to:
- Wetmore et al. (2015) "Rapid quantification of mutant fitness in diverse bacteria by sequencing randomly barcoded transposons" *mBio*
- Price et al. (2018) "Mutant phenotypes for thousands of bacterial genes of unknown function" *Nature*

## Development

### Local Setup

```bash
# Clone the repository
git clone https://github.com/justaddcoffee/fitness-mcp.git
cd fitness-mcp

# Install development dependencies
uv sync --dev
```


## License

BSD-3-Clause
