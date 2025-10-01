# eQTL Summary Statistics Service

## Overview

This project provides an ETL (Extract, Transform, Load) pipeline built using Apache Spark, which processes data files, extracts information, and loads it into a MongoDB database. The pipeline runs in a Dockerized environment, utilizing multiple services including MongoDB and Spark.

## Project Structure

```
.
├── spark
│   ├── __init__.py
│   ├── Dockerfile
│   ├── log4j.properties
│   ├── spark_app.py
│── utils
│   ├── __init__.py
│   ├── constants.py
│   ├── requirements.txt
│   └── utils.py
├── .gitignore
├── docker-compose.yml
├── format-lint
├── pytype.cfg
├── README.md
└── requirements.dev.txt
```

### Key Files and Directories

- **spark/**: Contains the main Spark application and supporting files.
  - **spark_app.py**: The main script that runs the ETL process.
  - **Dockerfile**: Defines the Docker image for the Spark application.
  - **log4j.properties**: Configuration file for logging in Spark.
- **utils/**: Utility functions and constants used in the ETL process.  
- **docker-compose.yml**: Orchestrates the Docker containers for MongoDB, Spark Master, Spark Worker, and the Spark application.

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Python 3.8 or higher
- Java 8 or higher (for Apache Spark)

### Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/EBISPOT/eqtl-sumstats-service.git
   cd eqtl-sumstats-service
   ```

2. Build and start the Docker containers:

   ```bash
   docker-compose build
   docker-compose up
   ```

   This will pull the necessary Docker images, build the custom Spark application image, and start the services (MongoDB, Spark Master, Spark Worker, Spark Application).

### Running the ETL Pipeline

The ETL pipeline is automatically triggered when the Spark application container starts. The `spark_app.py` script performs the following tasks:

1. **Download**: Fetches data files from a remote FTP server.
2. **Process**: Parses and transforms the data using Spark.
3. **Load**: Writes the processed data into a MongoDB collection.

### Configuration

- **FTP Configuration**: FTP connection details are defined in the `constants.py` file.
- **MongoDB Configuration**: MongoDB connection URI and database details are also specified in `constants.py`.
- **Spark Configuration**: Custom configurations for the Spark session, including MongoDB integration, are set in `spark_app.py`.


## Development

It might be a good idea to limit dataframes to 10 rows in spark. Otherwise it might be a problem in your local development. One can search for `DEV` for such points. 

### Linting and Formatting

Create a virtual env for format & lint in which you can install the required Python packages using:

```bash
pip install -r requirements.dev.txt
```

One can run the script as follows:

```bash
./format-lint
```
