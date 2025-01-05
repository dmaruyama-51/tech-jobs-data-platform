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
        to_hex(md5(tool)) as tool_id,
        tool
    from
        stg_joblist, unnest(tool) as tool
    group by
        1, 2
)

select * from final
