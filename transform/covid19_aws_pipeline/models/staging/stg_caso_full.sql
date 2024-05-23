{{ config(materialized='table') }}

with source as (
    select 
        city,
        city_ibge_code,
        date,
        epidemiological_week,
        estimated_population,
        estimated_population_2019,
        is_last,
        is_repeated,
        last_available_confirmed,
        last_available_confirmed_per_100k_inhabitants,
        last_available_date,
        last_available_death_rate,
        last_available_deaths,
        order_for_place,
        place_type,
        state,
        new_confirmed,
        new_deaths
    from {{ source('athena', 'caso_full') }}
)

select *
from source;