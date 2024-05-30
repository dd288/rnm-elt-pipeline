select
    ex.ep_id,
    ex.char_id,
    cr.origin_id,
    cr.location_id,
from
    {{ ref('int_ram_exploded') }} as ex
left join
    {{ ref('int_ram_fact') }} as cr on cr.char_id = ex.char_id