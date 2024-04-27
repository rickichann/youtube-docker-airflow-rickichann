# docker-airflow-rickichann

## Module 1: How to install Airflow on Docker | Setting Up Airflow with Docker-Compose in 3 Minutes
- Download docker and install [Docker](https://www.docker.com/products/docker-desktop/)
- Create a folder and inside the folder create .env and docker-compose.yml files
- Copy and paste the .env dan docker-compose.yml
- Open your terminal, type pip ```docker-compose up -d```, and press enter.

## Module 2: ETL Scheduling from PostgreSQL to PostgreSQL with Airflow.
- Insert data into PostgreSQL
  - Open your terminal, type ``jupyter notebook`` If you haven't installed it yet, you can see it in this tutorial [Jupyter Notebook](https://www.youtube.com/watch?v=ENApxFALR7M).
  - Create new .ipynb file
  - Copy and paste this file nyc_ingestion.py and run the code.
- Access to database with TablePlus
  - Database Configuration:
  ```
    - host: localhost
    - port: 5434
    - user: airflow
    - password: airflow
    - database: 
  ```
  - Press ```CMD + K``` or ``` CTRL + K ``` or icon database on top
  - Create "New" we will create two databases, namely master_db and warehouse_db.
