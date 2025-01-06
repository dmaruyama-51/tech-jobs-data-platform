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
        to_hex(md5(framework)) as framework_id,
        framework
    from
        stg_joblist,
        unnest(framework) as framework
    group by
        1, 2
)

select * from final
