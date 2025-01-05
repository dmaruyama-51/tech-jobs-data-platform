{{
  config(
    materialized='view'
  )
}}

with

stg_joblist as (
    select
        job_id,
        framework
    from {{ ref('stg_joblist') }}
),

final as (
    select
        job_id,
        to_hex(md5(framework)) as framework_id
    from
        stg_joblist,
        unnest(framework) as framework
)

select * from final
