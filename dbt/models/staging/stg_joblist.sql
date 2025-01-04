{{
  config(
    materialized='view'
  )
}}

with source as (
    select *
    from {{ source('bigdata_navi', 'lake__joblist') }}
),

staged as (
    select
        detail_link,
        listing_start_date,
        monthly_salary,
        occupation,
        work_type,
        work_location,
        industry,
        job_content,
        required_skills,
        preferred_skills,
        rate_of_work,
        job_title,
        to_hex(md5(detail_link)) as job_id,
        split(programming_language, '\n') as programming_language,
        split(tool, '\n') as tool,
        split(framework, '\n') as framework,
        safe_cast(regexp_extract(number_of_recruitment_interviews, r'(\d+)') as int64)
            as number_of_recruitment_interviews,
        safe_cast(regexp_extract(number_of_days_worked, r'週(\d+)日') as int64) as number_of_days_worked,
        safe_cast(regexp_extract(number_of_applicants, r'(\d+)') as int64) as number_of_applicants
    from source
)

select * from staged
