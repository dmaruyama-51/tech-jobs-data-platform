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
        detail_link,
        job_title,
        occupation,
        work_type,
        work_location,
        industry,
        job_content,
        required_skills,
        preferred_skills
    from
        stg_joblist
)

select * from final
