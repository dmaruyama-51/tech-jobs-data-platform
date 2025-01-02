# tech-jobs-data-platform

## Overview
tech-jobs-data-platform is a data infrastructure system for analyzing technology-related job data. It provides a mechanism for scraping data from job sites and leveraging Google Cloud Platform (GCP) to efficiently manage and analyze the data.


## Technical Stack

### Cloud Services (GCP)
- **Cloud Run Functions (2nd gen)**
- **Cloud Storage** for source code and scraped data
- **Cloud Pub/Sub** for event-driven architecture
- **Cloud Scheduler** for daily execution
- **BigQuery** for data warehousing

### Infrastructure as Code
- **Terraform** for GCP resource provisioning
  - GCS backend for state management
  - Environment separation (dev/prod)

### Development Tools
- **Poetry** for dependency management
- **Ruff** for linting and formatting
- **MyPy** for type checking


## Functions & Executing Flow

The system integrates multiple GCP services to create the following workflow, enabling automated data collection and processing:

### Scraping Process
The scraping workflow runs daily to collect fresh job posting data:

```Mermaid
graph LR
    A[Cloud Scheduler] -->|Daily at 5 AM| B[Pub/Sub Topic: job-scraper-topic]
    B -->|Push Notification| C[Pub/Sub Subscription]
    C -->|HTTP POST| D[Cloud Function: func_scraper]
    D -->|Execute Scraping| E[Recuiting Site]
    E -->|Retrieve Data| D
    D -->|Save CSV| F[Cloud Storage]
```

### Loading Process

When new data is saved to Cloud Storage, it automatically triggers the loading process to BigQuery:

```Mermaid
graph LR
    A[Cloud Storage] -->|New File Creation| B[Storage Notification]
    B -->|Event Notification| C[Pub/Sub Topic: job-loader-trigger-topic]
    C -->|Push Notification| D[Pub/Sub Subscription]
    D -->|HTTP POST| E[Cloud Function: func_loader]
    E -->|Read Data| F[Cloud Storage]
    E -->|Load Data| G[BigQuery]
```

## Development Setup

1. Clone the repository and install dependencies:

```bash
git clone https://github.com/your-repo/tech-jobs-data-platform.git
cd tech-jobs-data-platform
poetry install
```

2. Configure GCP credentials:

```bash
gcloud auth application-default login
```

3. Create env files and set your PROJECT_ID:

```
# functions/.env
PROJECT_ID=your-project-id-dev

# terraform/env/dev.tfvars
project_id = your-project-id-dev
region     = youer-gcp-region-dev

# terraform/env/prod.tfvars
project_id = your-project-id-prod
region     = youer-gcp-region-prod
```

### Local Development 

1. linting and formatting 

```bash
# python 
make lint
make format

# terraform 
make tf-check
```

2. Run Cloud Functions locally:

```bash
# run scraper or loader function
make run-scraper
make run-loader

# test function 
curl http://localhost:8080
```

3. Run Terraform for development environment:

```bash
make tf-init-dev
make tf-apply-dev
```


### Production Deployment

```bash
make tf-init-prod
make tf-apply-prod
```
