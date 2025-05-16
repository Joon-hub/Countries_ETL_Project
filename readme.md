# Countries ETL Project

A comprehensive ETL (Extract, Transform, Load) pipeline for collecting, processing, and storing countries data from REST API.

## Overview

This project implements a robust ETL pipeline that extracts countries data from REST API, transforms it into a consistent format, and loads it into a database for analysis and visualization.

## Project Structure
```
Countries_ETL_Project/
├── artifacts/           
│   └── rdl.png          # Data lineage or schema diagram
├── config/              
│   └── settings.py      # DB connection settings
├── Database/            
│   ├── __init__.py      
│   ├── connection.py    # Database connection handling
│   └── load.py          # Data loading utilities
├── etl/                 
│   ├── __pycache__/     
│   ├── __init__.py      
│   ├── extract.py       # Data extraction module
│   ├── sample_data.py   # Sample data for testing
│   └── transform.py     # Data transformation module
├── SQL/                 
│   ├── DB_Schema.sql    # Database schema definition
│   └── query.sql        # SQL queries for analysis
├── utils/               
├── .env                 
├── main.py              
├── Pipfile              
├── Pipfile.lock         
└── readme.md            
```

## ✨ Features

- **Data Extraction**: Fetch countries data from REST APIs using `etl/extract.py`
- **Data Transformation**: Clean, normalize, and enrich raw data with `etl/transform.py`
- **Data Loading**: Store processed data in a database via `Database/load.py`
- **Data Analysis**: Run analytics queries on the stored data
- **Flexible Configuration**: Easily configurable pipeline components

## Configuration

The pipeline can be configured through the `config/` directory and `.env` file:

- **Data Sources**: Configure API endpoints and credentials
- **Transformation Rules**: Define how data should be processed
- **Database Connection**: Set up database connection parameters
- **Logging**: Configure logging levels and destinations

## Data Flow

1. **Extract**: Data is extracted from various sources (APIs, files, etc.)
2. **Transform**: Raw data is cleaned, normalized, and enriched
3. **Load**: Processed data is loaded into the database
4. **Analyze**: SQL queries can be run to analyze the stored data

