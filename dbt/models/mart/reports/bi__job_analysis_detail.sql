{{
  config(
    materialized='table'
  )
}}

with

/* ==============================
    Import CTE
============================== */
fct_jobs as (
    select * from {{ ref('fct_jobs') }}
),

dim_job_details as (
    select * from {{ ref('dim_job_details') }}
),

dim_date as (
    select * from {{ ref('dim_date') }}
),

dim_language as (
    select * from {{ ref('dim_language') }}
),

dim_tool as (
    select * from {{ ref('dim_tool') }}
),

dim_framework as (
    select * from {{ ref('dim_framework') }}
),

bridge_language as (
    select * from {{ ref('bridge_language') }}
),

bridge_tool as (
    select * from {{ ref('bridge_tool') }}
),

bridge_framework as (
    select * from {{ ref('bridge_framework') }}
),

/* ==============================
    Logical CTE
============================== */

lang as (
    select
        bl.job_id,
        bl.lang_id,
        dl.lang
    from
        bridge_language as bl
    left join dim_language as dl
        on bl.lang_id = dl.lang_id
),

tool as (
    select
        bt.job_id,
        bt.tool_id,
        dt.tool
    from
        bridge_tool as bt
    left join dim_tool as dt
        on bt.tool_id = dt.tool_id
),

framework as (
    select
        bf.job_id,
        bf.framework_id,
        df.framework
    from
        bridge_framework as bf
    left join dim_framework as df
        on bf.framework_id = df.framework_id
),

final as (
    select
        f.job_id,
        l.lang_id,
        t.tool_id,
        fw.framework_id,

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

        l.lang,
        t.tool,
        fw.framework,

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
    left join lang as l
        on f.job_id = l.job_id
    left join tool as t
        on f.job_id = t.job_id
    left join framework as fw
        on f.job_id = fw.job_id
)

select * from final
