select
    id as ep_id,
    name as ep_name,
    episode as ep_num,
    characters as ep_char,
    created,
from
    {{ source('ram', 'episodes') }}