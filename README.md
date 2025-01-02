# tech-jobs-data-platform

## Overview
tech-jobs-data-platform is a data infrastructure system for analyzing technology-related job data. It provides a mechanism for scraping data from job sites and leveraging Google Cloud Platform (GCP) to efficiently manage and analyze the data.

## Features

Running these features on Cloud Run Functions
- Scraping data from job sites（`func_scraper`）
- Loading data to BigQuery（`func_loader`）

Planned
- Implementation of Dimensional Modeling using dbt


## Executing Flow

The system integrates multiple GCP services to create the following workflow:

1. Scraping

```mermaid
graph LR
    A[Cloud Scheduler] -->|Daily at 5 AM| B[Pub/Sub Topic: job-scraper-topic]
    B -->|Push Notification| C[Pub/Sub Subscription]
    C -->|HTTP POST| D[Cloud Function: func_scraper]
    D -->|Execute Scraping| E[Recuiting Site]
    E -->|Retrieve Data| D
    D -->|Save CSV| F[Cloud Storage]
```

2. Loading

```mermaid
graph LR
    A[Cloud Storage] -->|New File Creation| B[Storage Notification]
    B -->|Event Notification| C[Pub/Sub Topic: job-loader-trigger-topic]
    C -->|Push Notification| D[Pub/Sub Subscription]
    D -->|HTTP POST| E[Cloud Function: func_loader]
    E -->|Read Data| F[Cloud Storage]
    E -->|Load Data| G[BigQuery]
```
