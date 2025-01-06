{{
  config(
    materialized='table'
  )
}}

with

fct_jobs as (
    select * from {{ ref('fct_jobs') }}
),

dim_job_details as (
    select * from {{ ref('dim_job_details') }}
),

dim_date as (
    select * from {{ ref('dim_date') }}
),

final as (
    select
        f.job_id,
        f.monthly_salary,
        f.number_of_recruitment_interviews,
        f.number_of_days_worked,
        f.number_of_applicants,

        jd.job_title,
        jd.detail_link,
        jd.occupation,
        jd.work_type,
        jd.work_location,
        jd.industry,
        jd.job_content,
        jd.required_skills,
        jd.preferred_skills,

        f.listing_start_date,
        d.day_of_week_name_short as listing_day_of_week,
        d.week_start_date as listing_week,
        d.month_start_date as listing_month,
        d.quarter_start_date as listing_quarter,
        d.year_start_date as listing_year

    from fct_jobs as f
    left join dim_job_details as jd
        on f.job_id = jd.job_id
    left join dim_date as d
        on f.listing_start_date = d.date_day
)

select * from final
