with source as (
    select *
    from {{ source('lake__bigdata_navi', 'joblist') }}
),

staged as (
    select
        -- 後ほど整形
        *
    from source
)

select * from staged