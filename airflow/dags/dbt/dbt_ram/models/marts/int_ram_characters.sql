select
    char_id,
    char_name,
    species,
    gender,
    char_type,
    status,
    image,
from
    {{ ref('stg_ram_characters') }}