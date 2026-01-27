# Slim Solr Project Readme Documentation

## Overview

The Slim Solr project is a specialized Solr index for GWAS catalog data. It generates JSON documents essential for the GWAS Slim Solr index, including Publication, Study, Variant, Trait and Gene.

## Features

1. **JSON Document Generation**: The `generate_solr_docs.py` script is designed to create JSON documents representing key information needed for the GWAS Slim Solr index. It efficiently handles the generation of documents for Publication, Study, Variant, Trait and Gene.

1. **Flexible Usage**: The script includes command-line options to specify database and data type parameters, allowing for tailored usage depending on specific project requirements.

1. **Automated Document Creation**: Facilitates the automated creation of Solr index documents, streamlining the process of indexing GWAS data.

1. **Integration with GWAS Solr Slim Deployment**: Seamlessly integrates with the existing deployment and management processes, including conda environment activation and Bamboo automation pipelines for Slim Solr release tasks.

## Requirements

- Access to an EBI server (specifically for the GWAS domain).
- Virtual environment setup on the EBI server.

## Deployment Steps

The deployment of the GWAS Solr Slim project to High-Performance Computing (HPC) clusters involves a series of steps, managed through a CI/CD pipeline defined in `.gitlab-ci.yml`. This process is critical for ensuring that the codebase, hosted on GitHub and mirrored internally on GitLab, is efficiently and securely deployed.

### Continuous Integration/Deployment

- The CI/CD pipeline, hosted on GitLab, mirrors the GitHub repository and uses the pipeline for deployment.
- Pipeline Definition: [GitLab CI Pipeline](https://gitlab.ebi.ac.uk/gwas/gwas-utils/-/ci/editor?branch_name=master)

### Pipeline Stages

1. **Build Stage**: Involves compiling the code and building the Docker image.
2. **Deploy Stage**: Focuses on deploying the built image to the HPC cluster.

### Pipeline Configuration

- **General Setup**:
  - Image: `docker:latest`
  - Services: `docker:dind`
  - Key Variables: `DOCKER_DRIVER`, `DOCKER_TLS_CERTDIR`, `DOCKER_HOST`, `CI_REGISTRY_IMAGE`

- **Build Stage**:
  - Triggered by commits to `master` and `dev` branches.
  - Involves Docker Hub login, image pulling and building, and pushing to the registry.

- **Build Release**:
  - Activated by new tags.
  - Similar Docker operations, with added tagging of images as 'latest'.

- **Deploy Dev**:
  - Triggered by commits to `master` and `dev`.
  - Involves SSH environment setup, server connection, environment activation, and package installation from GitHub.

- **Deploy Prod**:
  - Triggered by new tags.
  - Similar to Deploy Dev, but connects to the prod server.

## Running the Project Locally

### Prerequisites

- VPN Access: Ensure you have VPN access to connect to the database, as database access is restricted.
- Git: Required for cloning the repository.
- Python 3: The scripts are Python-based, so Python 3 is needed.
- Virtual Environment: For isolating the project dependencies.

### Steps to Run Locally

1. **Clone the Repository**: Start by cloning the Slim Solr project from GitHub.

   ```bash
   git clone https://github.com/EBISPOT/gwas-solr-slim.git
   cd gwas-solr-slim
   ```

2. **Create and Activate Virtual Environment**:
   - For creation:

     ```bash
     python3 -m venv .venv
     ```

   - Activation (choose according to your platform):
     - POSIX systems (Linux, MacOS, etc.):

       ```bash
       source .venv/bin/activate
       ```

     - Windows Command Prompt:

       ```bash
       .venv\Scripts\activate.bat
       ```

     - Windows PowerShell:

       ```bash
       .venv\Scripts\Activate.ps1
       ```

3. **Install Dependencies**:
   - Install the GWAS database connection module from the private GitLab repository and other required dependencies:

     ```bash
     pip install git+ssh://git@gitlab.ebi.ac.uk/gwas/gwas_db_connect.git
     pip install -r requirements.txt
     ```

4. **Test the Script**:
   - Verify the script setup:

     ```bash
     python scripts/generate_solr_docs.py --help
     ```

   - Try running the script with specified parameters (replace `<some/dir/>` with your target directory):

     ```bash
     python scripts/generate_solr_docs.py --database DEV3 --limit 1 --test --targetDir <some/dir/>
     ```

## How to Contribute

### Contribution Process

- Identify existing issues in the project that you can resolve. Contributions that address these issues are highly appreciated.
- The project is open to all kinds of improvements. Feel free to propose changes that you believe will benefit the project. These could include code optimizations, resource management improvements, or any other relevant changes.
- Test your changes thoroughly in your local environment before submitting them.
- **Submitting Pull Requests**:
  - If you have improvements or new features, submit them as pull requests.
  - Make sure your PRs are based on the `dev` branch.
  - Follow the standard Git workflow for your contributions. This includes forking the repository, creating a new branch for your changes, and then submitting a PR.

- **PR Review and Integration**:
  - Once a PR is submitted to the `dev` branch, it undergoes a review process.
  - After approval and merging into `dev`, changes are then merged into the `master` branch.

### Release Process

- When the team decides to release a new version, the relevant commit in the `master` branch is tagged.
- This tagged commit is then recognized by the mirrored GitLab repository, initiating the deployment process as outlined in the CI/CD pipeline.