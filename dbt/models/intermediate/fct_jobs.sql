{{
  config(
    materialized='view'
  )
}}

with

stg_joblist as (
    select *
    from {{ ref('stg_joblist') }}
),

final as (
    select
        job_id,
        listing_start_date,
        monthly_salary,
        number_of_recruitment_interviews,
        number_of_days_worked,
        number_of_applicants
    from
        stg_joblist
)

select * from final
