# SPOT Apps Stats Service

This service is storing the access logs of all the SPOT applications. The service collects access logs from Elasticsearch(EBI Meter Service), processes them, stores them in a DB and provides a user-friendly web interface to interact with the data.

At the moment, the app fetches weblogs and ftplogs from the elastic search index.

## Overview

The SPOT Apps Stats Service consists of three main components:

1. **Data Ingestion Service**: Fetches access logs from Elasticsearch and stages them for processing
2. **Data Processing Service**: Processes staged logs and loads them into a PostgreSQL database
3. **Web Application**: Provides a user interface for querying the statistics

## Architecture

The application follows a modern, scalable architecture:

- **Frontend**: React with Tailwind CSS and shadcn/ui components
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Data Processing**: Python-based ETL pipeline
- **Configuration**: YAML-based resource configuration

This is how the architecture look like:

![General Architecture-SPOT-Stat-APP-2024-12-13-150853](https://github.com/user-attachments/assets/668aa65a-f206-47b2-91fe-fd8fbaf6ab77)

## Prerequisites

- Python >= 3.7
- Node.js >= 16
- PostgreSQL >= 16
- Access to Elasticsearch instance containing SPOT apps logs

## Setup

### Database Setup

1. Create a PostgreSQL database
2. Run the database initialization script:
```bash
psql -d your_database_name -f app-stat-db-creation.sql
```

### Environment Configuration

Create a `.env` file in the project root with the following variables:
```
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
ES_HOST=your_elasticsearch_host
ES_USER=your_elasticsearch_user
ES_PASSWORD=your_elasticsearch_password
STAGING_AREA_PATH=./staging
```

`STAGING_AREA_PATH` is where the logs downloaded from the elastic search will be stored.

### Python Virtual Environment Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```
### Fetch Data from ElasticSearch
```bash
cd dataload
python fetch-data-from-api.py {no_of_days_param}
```

You can pass an optional `no_of_days_param` to the script. If nothing is provided the value will be 1 day i.e. 24 Hours


### Load Data to DB Setup

```bash
cd dataload
python load-data.py
```

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Start the FastAPI server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

If you run into some dependency issues then you can try running:

```bash
npm install --legacy-peer-deps
```

3. Start the development server:
```bash
npm run dev
```

The web interface will be available at `http://localhost:3000`

This how the frontend looks like:

![Screenshot 2024-12-13 at 15 37 54](https://github.com/user-attachments/assets/771f62be-d93a-4319-a4e1-d992b59aaa26)

## Data Pipeline

### Fetching Data

To fetch new data from Elasticsearch:
```bash
python fetch-data-from-api.py
```

### Processing Staged Data

To process staged data and load it into the database:
```bash
python load-data.py
```

## Resource Configuration

Create a `config.yaml` file to specify the resources and endpoints to track:

```yaml
resources:
  - name: GWAS
    endpoints:
      - "www.ebi.ac.uk/gwas/*"
  - name: OLS
    endpoints:
      - "www.ebi.ac.uk/ols4/*"
```

In this the pattern of the URL you would need to specify the depth of the url paths you want to fetch the data till.
