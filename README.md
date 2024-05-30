<div align="center">
  
  # Rick and Morty ELT
  
</div>

<div align="center">
  <img src="https://github.com/dd288/rnm-elt-pipeline/blob/main/images/rick.jpg" alt="Rick and Morty Characters" style="width:50%;"/>
</div>

<div align="center">
  
  [About](#about) | [Overview](#overview) | [Installation](#installation) |  [Improvements](#improvements)
  
</div>

## About

This **ELT pipeline** is designed to process data from the **[Rick and Morty API](https://rickandmortyapi.com/)**, including information about characters, locations, and episodes. The pipeline starts by extracting data using **Airbyte**, which pulls information directly from the API. This data is then stored in MinIO, using it as a datalake

Within MinIO, the data undergoes transformations following the **[medallion architecture](https://dataengineering.wiki/Concepts/Medallion+Architecture)**. This approach structures the data into three layers: **Bronze (raw data), Silver (cleaned data), and Gold (aggregated data)**, ensuring that each stage is progressively more refined and ready for analysis.

Once transformed, the data is loaded into a **Snowflake** warehouse using **Airbyte** again. In Snowflake, dbt (data build tool) is employed to model the data, making it easier to query and analyze. The final, modeled data is visualized with Streamlit, creating interactive and dynamic dashboards for exploring the rich details of the Rick and Morty universe.

The entire process is orchestrated by **Apache Airflow**, with the **_Cosmos Astronomer_** library enhancing workflow management. Docker is used to containerize all components, ensuring a consistent and reliable environment for the pipeline to run smoothly. This comprehensive setup allows for efficient extraction, transformation, and visualization of Rick and Morty data, providing valuable insights into the series.

## Overview

### Streamlit App

![alt text](https://github.com/dd288/rnm-elt-pipeline/blob/main/images/streamlit_app.gif "Streamlit GIF")

#### ELT Diagram

![alt text](https://github.com/dd288/rnm-elt-pipeline/blob/main/images/API.png "ELT Diagram")

### Airflow Graph

![alt text](https://github.com/dd288/rnm-elt-pipeline/blob/main/images/airflow_graph.png "Airflow Graph")

### Key Technologies

* [Apache Airflow (Cosmos - Astronomer)](https://www.astronomer.io/cosmos/): Orchestration
* [Docker](https://www.docker.com/): Containerization
* [Airbyte](https://airbyte.com): Moving Data
* [Pandas](https://pypi.org/project/pandas/): Transformation & Cleaning
* [MinIO](https://min.io/): Datalake
* [Snowflake](https://www.snowflake.com/en/): Data Warehouse
* [dbt](https://www.getdbt.com/): Staging & Modelling
* [Streamlit](https://streamlit.io/): Visualization

### Installation

1. Use [git](https://git-scm.com/) to clone the repository
2. Install docker
3. Install the astro-cli
4. Install Airbyte
5. Configure airbyte & import the airbyte yaml file
6. Start all the containers
7. Run the streamlit app

### Improvements

The installation process can be dramatically improved by create a Dockerfile & docker compose. Also terraform can be added to automate the connection process.

Another addition could be pySpark for better data processing, but I don't see the need with data quantity and quality. 