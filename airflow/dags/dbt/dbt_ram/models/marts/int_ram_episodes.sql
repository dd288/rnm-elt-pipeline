select
    ep_id,
    ep_name,
    ep_num,
from    
    {{ ref('stg_ram_episodes') }}