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
        to_hex(md5(lang)) as lang_id,
        lang
    from
        stg_joblist,
        unnest(programming_language) as lang
    group by
        1, 2
)

select * from final
