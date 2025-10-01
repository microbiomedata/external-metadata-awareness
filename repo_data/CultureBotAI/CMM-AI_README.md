# CMM-AI: Lanthanide Bioprocessing Data Pipeline

## 🔬 Project Overview

This project develops an automated data pipeline for **lanthanide bioprocessing research**, focusing on rare earth element-dependent biological processes in microorganisms. The pipeline integrates multiple biological databases to create comprehensive research datasets from small seed collections.

### Scientific Focus: Lanthanide-Dependent Biology

Lanthanides (rare earth elements) play crucial roles in microbial metabolism, particularly in:
- **XoxF methanol dehydrogenase** systems (lanthanide-dependent enzymes)
- **Methylotrophic bacteria** (Methylobacterium, Methylorubrum, Paracoccus)
- **Environmental metal cycling** and biogeochemistry
- **Siderophore/lanthanophore** transport mechanisms
- **PQQ-dependent enzyme** complexes

### Current Status: First Draft Data (v0.1)

⚠️ **Important**: The current datasets represent a **first draft and initial round** of data collection. This is an evolving research pipeline with:
- **Proof-of-concept data extension** from seed datasets
- **Initial database integration** and URL generation
- **Baseline automation** for reproducible workflows
- **Foundation for iterative improvement** and refinement

Future versions will include expanded search terms, refined filtering criteria, manual curation, and domain expert validation.

## 🌟 Technical Features

- **📊 Automated Data Extension**: Transform small datasets (2-17 rows) into comprehensive research databases (15-132 rows)
- **🔗 Download URL Generation**: Direct links to NCBI, KEGG, UniProt, PDB, and other databases
- **🧬 Multi-Database Integration**: NCBI Assembly/BioSample, KEGG pathways, UniProt proteins, PDB structures
- **🔄 Pipeline Automation**: Complete Makefile workflow for reproducible research
- **📄 File Format Support**: Excel to TSV, Word/PDF to text conversion
- **🤖 AI-Ready**: Structured for Claude Code and other AI tools

## 📋 Data Tables Extended (First Draft)

| Table | Original → Extended | Description |
|-------|-------------------|-------------|
| **Genomes** | 2 → 65 rows | Lanthanide-relevant bacteria/archaea genomes with annotation URLs |
| **Biosamples** | 17 → 132 rows | Environmental samples with NCBI download links |
| **Pathways** | 1 → 9 rows | KEGG and MetaCyc metabolic pathways with direct access |
| **Genes/Proteins** | 3 → 29 rows | Curated protein sequences from UniProt/KEGG |
| **Structures** | 1 → 17 rows | PDB crystal structures and AlphaFold predictions |
| **Publications** | 2 → 22 rows | Peer-reviewed literature from PubMed/PMC |
| **Datasets** | 2 → 15 rows | Research datasets from multiple repositories |

*Note: These numbers represent initial automated extension. Future iterations will include expert curation and validation.*

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/CultureBotAI/CMM-AI.git
cd CMM-AI

# Install dependencies
make install

# Convert original Excel files to TSV
make convert-excel

# Run the full pipeline
make update-all
```

### Individual Pipeline Steps

```bash
# Update specific tables
make update-genomes      # Extend genomes with NCBI data
make update-biosamples   # Extend biosamples with NCBI data
make update-pathways     # Extend pathways with KEGG/MetaCyc
make update-datasets     # Extend datasets with repository links
make update-genes        # Extend genes/proteins with UniProt/KEGG
make update-structures   # Extend structures with PDB/AlphaFold
make update-publications # Extend publications with PubMed/PMC

# View pipeline status
make status
```

## 📁 Repository Structure

```
CMM-AI/
├── 📂 src/                          # Python source code
│   ├── 🐍 parsers.py               # File conversion utilities
│   ├── 🐍 ncbi_search.py           # NCBI database integration
│   ├── 🐍 pathway_search.py        # KEGG/MetaCyc pathway search
│   ├── 🐍 gene_search.py           # UniProt/KEGG gene search
│   ├── 🐍 structure_search.py      # PDB/AlphaFold structure search
│   ├── 🐍 dataset_search.py        # Multi-repository dataset search
│   ├── 🐍 publication_search.py    # PubMed/PMC literature search
│   └── 🐍 extend_*.py              # Pipeline automation scripts
├── 📂 data/                         # Research data
│   ├── 📂 sheet/                   # Original Excel files
│   ├── 📂 txt/sheet/               # Converted TSV files + extensions
│   ├── 📂 publications/            # PDF research papers
│   └── 📂 proposal/                # Project documentation
├── ⚙️ Makefile                     # Pipeline automation
├── 📋 pyproject.toml               # Package configuration
└── 📚 CLAUDE.md                    # AI assistant guidance
```


## 🔗 Database Integrations

### NCBI APIs
- **Assembly Database**: Genome sequences and annotations
- **BioSample Database**: Environmental sample metadata
- **PubMed/PMC**: Scientific literature

### Other APIs
- **KEGG REST**: Metabolic pathways and enzyme data
- **UniProt REST**: Protein sequences and annotations
- **RCSB PDB**: Crystal structures and experimental data
- **AlphaFold**: Predicted protein structures

## 📊 Data Pipeline Details

### Input Processing
1. **Excel Conversion**: Multi-sheet Excel files → Individual TSV files
2. **Document Parsing**: Word/PDF documents → Searchable text
3. **Filename Sanitization**: Spaces → underscores for consistency

### Data Extension Process
1. **NCBI Search**: Query Assembly/BioSample with lanthanide terms
2. **Literature Mining**: PubMed searches for relevant publications
3. **Pathway Mapping**: KEGG/MetaCyc pathway identification
4. **Structure Discovery**: PDB searches for protein structures
5. **URL Generation**: Direct download links for all data sources

### Quality Control
- **Rate Limiting**: Respects API usage guidelines
- **Duplicate Removal**: Based on unique identifiers
- **Error Handling**: Graceful degradation with informative messages
- **Validation**: Doctests and integration tests

## 🤖 AI Integration

### Claude Code Support
- **CLAUDE.md**: Comprehensive guidance for AI assistants
- **Structured Documentation**: Clear file organization and conventions
- **Type Hints**: Full type annotation for better AI understanding
- **Doctest Examples**: Executable documentation

### GitHub AI Features
- **AI-powered workflows**: Automated code review and issue triage
- **Copilot integration**: Smart code completion and suggestions

## ⚡ Performance & Scalability

- **Parallel Processing**: Multiple API calls where possible
- **Caching**: Intelligent rate limiting and result storage
- **Incremental Updates**: Only fetch new data when needed
- **Batch Operations**: Efficient database queries

## 🧪 Development

### Running Tests
```bash
# Run all tests
make test

# Run specific validation
python -m doctest src/parsers.py -v
python -m doctest src/ncbi_search.py -v
```

### Code Quality
```bash
# Check code formatting (if ruff is configured)
uv run ruff check src/
uv run ruff format src/
```

## 📈 Data Statistics (First Draft)

### Growth Metrics
- **Total Rows Added**: 500+ new data entries (initial automated extension)
- **Database Coverage**: 7+ major biological databases integrated
- **Literature Coverage**: 20+ peer-reviewed publications (preliminary selection)
- **Structure Coverage**: PDB + AlphaFold predictions (proof-of-concept)

### API Usage
- **NCBI E-utilities**: ~100 queries per pipeline run
- **KEGG REST**: ~20 pathway queries
- **UniProt REST**: ~50 protein queries
- **Rate Limiting**: 0.5-1.0 second delays between calls

## 🤝 Contributing

We welcome contributions! This project uses:
- **Python 3.8+** with type hints
- **uv** for dependency management
- **Make** for pipeline automation
- **Git** with conventional commits

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `make test` to validate
5. Submit a pull request

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **NCBI** for comprehensive biological databases
- **KEGG** for metabolic pathway data
- **UniProt** for protein sequence databases
- **RCSB PDB** for structural biology data
- **Claude AI** for development assistance

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/CultureBotAI/CMM-AI/issues)
- **Documentation**: See `CLAUDE.md` for detailed technical guidance
- **Discussions**: [GitHub Discussions](https://github.com/CultureBotAI/CMM-AI/discussions)

---

**🔬 Built for lanthanide bioprocessing research • 🤖 AI-enhanced development • 📊 Data-driven discovery**