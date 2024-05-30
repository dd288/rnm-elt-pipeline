select
    id as char_id,
    name as char_name,
    species,
    gender,
    type as char_type,
    status,
    location_id,
    origin_id,
    image,
    created,
from
    {{ source('ram', 'characters') }}