# Source Data Analysis

Source Data Analysis is dedicated to a comprehensive analysis of data from multiple sources to explore various biological and medical associations. By comparing data across numerous databases, the aim is to uncover insights into commonalities, discrepancies, and patterns that exist within and between these datasets.

Key areas of focus include:
- **Gene-to-Disease (G2D)**
- **Gene-to-Phenotype (G2P)**
- **Disease-to-Phenotype (D2P)**

Additional categories and data sources are also explored, aiming to provide a comprehensive view of the intricate relationships in biomedical research.

## Documentation

For detailed documentation, please refer to [Documentation link](https://monarch-initiative.github.io/source-data-analysis/).

## Latest Release

The latest release can be found [here](https://github.com/monarch-initiative/source-data-analysis/releases).

## Focus Areas

| Focus Area        | # Sources Analyzed | Documentation                                                         | Latest Release        |
|-------------------|--------------------|-----------------------------------------------------------------------|------------------------|
| Gene to Disease   | 5                  | [G2D](https://monarch-initiative.github.io/source-data-analysis/g2d) |  [AUG 2024](https://github.com/monarch-initiative/source-data-analysis/releases/tag/2024-08-13) |

## Installation and Setup

To install and activate the virtual environment locally, please follow these steps:

1. **Clone the project repository from GitHub:**

   ```bash
   git clone https://github.com/monarch-initiative/source-data-analysis.git

2. **Navigate to the project directory in your terminal:**

    ```bash
    cd source-data-analysis

3. **Create a virtual environment:**

    ```bash
    python -m venv venv

4. **Activate the virtual environment:**

    For Windows:
    ```bash
    venv\Scripts\activate
     ```
    For Mac/Linux:
    ```bash
    source venv/bin/activate

5. **Install the required packages:**

    ```bash
    pip install -r requirements.txt

## Usage
To execute the project commands, you can use the make utility. Here are some example commands:

1. **Download source files:**

    ```bash
    make download_g2d_sources

2. **Run analysis:**

    ```bash
    make analyze_g2d_sources

## Contributing
Feel free to contribute to the project by submitting issues, pull requests, or suggestions.
