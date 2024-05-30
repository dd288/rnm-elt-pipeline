-- Explode the characters JSON array from the episodes table and extract character ID
WITH exploded_episodes AS (
    SELECT
        e.ep_id AS ep_id,
        e.ep_name AS ep_name,
        e.ep_num AS ep_num,
        e.created AS ep_created,
        char.value::STRING AS char_url
    FROM
        {{ ref('stg_ram_episodes') }} AS e,
        LATERAL FLATTEN(input => TRY_PARSE_JSON(e.ep_char)) char
),

-- Extract the character ID from the URL
extracted_ids AS (
    SELECT
        ep_id,
        ep_name,
        ep_num,
        ep_created,
        SPLIT_PART(char_url, '/', -1) AS char_id
    FROM
        exploded_episodes
)

-- Select specific columns from the extracted IDs
SELECT
    ep_id,
    ep_name,
    ep_num,
    ep_created,
    char_id
FROM
    extracted_ids
