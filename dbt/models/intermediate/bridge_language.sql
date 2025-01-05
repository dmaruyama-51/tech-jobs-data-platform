{{
  config(
    materialized='view'
  )
}}

with

stg_joblist as (
    select
        job_id,
        programming_language
    from {{ ref('stg_joblist') }}
),

final as (
    select
        job_id,
        to_hex(md5(lang)) as lang_id
    from
        stg_joblist,
        unnest(programming_language) as lang
)

select * from final
