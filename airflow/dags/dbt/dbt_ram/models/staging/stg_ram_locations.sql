select
    id as loc_id,
    name as loc_name,
    type as loc_type,
    dimension as loc_demension
from
    {{ source('ram', 'locations') }}