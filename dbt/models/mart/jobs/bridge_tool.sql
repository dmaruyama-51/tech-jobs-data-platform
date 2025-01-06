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
        to_hex(md5(tool)) as tool_id
    from
        stg_joblist, unnest(tool) as tool
)

select * from final
