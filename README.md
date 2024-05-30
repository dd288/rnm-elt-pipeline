# Rick and Morty ELT

About | Installation | Overview | Improvements

## About

This ELT pipeline is designed to efficiently handle data related to the "Rick and Morty" universe, focusing on characters, locations, and episodes. The pipeline employs modern data engineering tools and follows best practices to ensure seamless data extraction, transformation, and loading processes. Here’s a detailed overview of each component and its function within the pipeline:

*    Data Extraction (Airbyte):
⋅⋅⋅Rick and Morty API Integration: Data is extracted from the Rick and Morty API using Airbyte. This integration allows for the continuous and automated ingestion of data about characters, locations, and episodes from the popular animated series.

*    Data Lake Storage (MinIO):
        S3-Compatible Storage: The extracted data streams are stored in MinIO, an S3-compatible datalake. MinIO provides a scalable and secure environment for storing large datasets, ensuring that all extracted data is safely preserved.

*    Data Transformation (Medallion Architecture):
        Bronze, Silver, Gold Layers: Within the MinIO datalake, data undergoes a series of transformations following the medallion architecture:
            Bronze Layer: Raw data as ingested from the API.
            Silver Layer: Cleaned and structured data.
            Gold Layer: Aggregated and refined data, optimized for analysis.

*    Data Loading (Airbyte):
        Snowflake Warehouse: The transformed data is then loaded into Snowflake, a cloud-based data warehouse. Airbyte facilitates this process, ensuring that data is efficiently transferred and stored in Snowflake for further processing.

*    Data Modeling (dbt):
        Transformations and Models: In Snowflake, dbt (data build tool) is used to create data models. dbt enables the development of modular, reusable, and version-controlled data transformations, ensuring the integrity and usability of the data.

*    Data Visualization (Streamlit):
        Interactive Dashboards: The final data is visualized using Streamlit. Streamlit provides an intuitive platform to create interactive and dynamic dashboards, allowing users to explore and analyze the Rick and Morty data with ease.

*    Orchestration (Airflow with Cosmos Astronomer Library):
        Workflow Management: Apache Airflow orchestrates the entire pipeline, managing the scheduling and execution of tasks. The Cosmos Astronomer library enhances Airflow’s capabilities, ensuring reliable and efficient workflow management.

*    Containerization (Docker):
        Consistent Environment: Docker is used to containerize all components of the pipeline. This ensures that each part of the pipeline runs in a consistent and isolated environment, reducing the risk of compatibility issues and facilitating seamless deployment.

This pipeline provides a comprehensive solution for extracting, transforming, and analyzing data from the Rick and Morty API, enabling fans and analysts to gain deeper insights into the characters, locations, and episodes of the beloved series.