{{ config(materialized='table') }}

with stg_caso as (
    select 
        date,
        state,
        city,
        place_type,
        confirmed,
        deaths,
        order_for_place,
        is_last,
        estimated_population_2019,
        estimated_population,
        city_ibge_code,
        confirmed_per_100k_inhabitants,
        death_rate
    from {{ source('athena', 'caso') }}
)

select *
from source;