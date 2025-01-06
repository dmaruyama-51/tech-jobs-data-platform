# Data Transformation

This directory contains a dbt project that manages data transformation processes in BigQuery.

## Data Model Structure

```mermaid
erDiagram
    fct_jobs ||--|| dim_job_details : "job_id"
    fct_jobs ||--o{ bridge_language : "job_id"
    fct_jobs ||--o{ bridge_tool : "job_id"
    fct_jobs ||--o{ bridge_framework : "job_id"
    bridge_language }o--|| dim_language : "lang_id"
    bridge_tool }o--|| dim_tool : "tool_id"
    bridge_framework }o--|| dim_framework : "framework_id"

    fct_jobs {
        string job_id PK
        date listing_start_date
        integer monthly_salary
        integer number_of_recruitment_interviews
        integer number_of_days_worked
        integer number_of_applicants
    }

    dim_job_details {
        string job_id PK
        string detail_link
        string job_title
        string occupation
        string work_type
        string work_location
        string industry
        string job_content
        string required_skills
        string preferred_skills
    }

    bridge_language {
        string job_id FK
        string lang_id FK
    }

    dim_language {
        string lang_id PK
        string lang
    }

    bridge_tool {
        string job_id FK
        string tool_id FK
    }

    dim_tool {
        string tool_id PK
        string tool
    }

    bridge_framework {
        string job_id FK
        string framework_id FK
    }

    dim_framework {
        string framework_id PK
        string framework
    }
```

### Staging Layer
- **stg_joblist**: Standardization of raw data (lake__joblist)
  - String splitting (programming_language, tool, framework)
  - Numeric data type conversion
  - job_id generation (MD5 hash of detail_link)

### Mart Layer
#### Fact Tables
- **fct_jobs**: Quantitative information about job listings

#### Dimension Tables
- **dim_job_details**: Detailed job listing information
- **dim_language**: Programming language master
- **dim_tool**: Development environment and tools master
- **dim_framework**: Framework and library master

#### Bridge Tables (Many-to-Many Relationships)
- **bridge_language**: Jobs-Programming Languages
- **bridge_tool**: Jobs-Development Tools & Environments  
- **bridge_framework**: Jobs-Frameworks

## Usage

```bash
# build
make dbt-run-dev
make dbt-run-prod

# test
make dbt-test-dev
make dbt-test-prod
```
