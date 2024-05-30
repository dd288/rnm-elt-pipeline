import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="Rick&Morty Characters Informations",
    page_icon=":)",
    layout="wide",
)


# Establish connection to Snowflake
conn = st.connection("snowflake")

with open('style.css') as f:
    css = f.read()

# Load external CSS file
st.markdown(
    f'<style>{css}</style>',
    unsafe_allow_html=True
)

# Title of the app
st.markdown("<h1 class='centered-title'>Rick and Morty Characters Information</h1>", unsafe_allow_html=True)



# Query to get total counts
total_counts_query = """
SELECT 
    (SELECT COUNT(*) FROM airbyte_database.dbt_schema.int_ram_characters) AS total_characters,
    (SELECT COUNT(*) FROM airbyte_database.dbt_schema.int_ram_episodes) AS total_episodes,
    (SELECT COUNT(*) FROM airbyte_database.dbt_schema.int_ram_locations) AS total_locations;
"""

# Execute query
total_counts = pd.read_sql(total_counts_query, conn)

with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<h3 style='text-align: center;'>Total Characters</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 24px; text-align: center;'>" + str(total_counts['TOTAL_CHARACTERS'][0]) + "</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h3 style='text-align: center;'>Total Episdoes</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 24px; text-align: center;'>" + str(total_counts['TOTAL_EPISODES'][0]) + "</p>", unsafe_allow_html=True)
    with col3:
        st.markdown("<h3 style='text-align: center;'>Total Locations</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 24px; text-align: center;'>" + str(total_counts['TOTAL_LOCATIONS'][0]) + "</p>", unsafe_allow_html=True)

# Query to get character names
characters_query = """
SELECT CHAR_ID, CHAR_NAME 
FROM airbyte_database.dbt_schema.int_ram_characters;
"""

characters_df = pd.read_sql(characters_query, conn)

with st.container(height=500, border=True):
    coln1,coln2,coln3 = st.columns(3)
    
    with coln1:
        # Dropdown menu for character selection
        st.markdown('<style>.stSelectbox > div { width: 54% !important; }</style>', unsafe_allow_html=True)
        character_name = st.selectbox("Select a character", characters_df['CHAR_NAME'])
        
        #character_name = st.selectbox("Select a character", characters_df['CHAR_NAME'], key="selectbox", class_="custom-selectbox")

        # Query to get character details
        # Query to get character details
# Query to get character details
        character_details_query = f"""
        SELECT 
            c.CHAR_NAME, c.CHAR_TYPE, c.GENDER, c.IMAGE, c.SPECIES, c.STATUS, 
            loc.LOC_NAME AS LOCATION, 
            org.LOC_NAME AS ORIGIN
        FROM airbyte_database.dbt_schema.int_ram_characters c
        JOIN airbyte_database.dbt_schema.fact_ram f ON c.CHAR_ID = f.CHAR_ID
        LEFT JOIN airbyte_database.dbt_schema.int_ram_locations loc ON loc.LOC_ID = TRY_CAST(f.LOCATION_ID AS INTEGER)
        LEFT JOIN airbyte_database.dbt_schema.int_ram_locations org ON org.LOC_ID = TRY_CAST(f.ORIGIN_ID AS INTEGER)
        WHERE c.CHAR_NAME = '{character_name}';
        """
        
        character_details_df = pd.read_sql(character_details_query, conn)
        character_details = character_details_df.iloc[0]
        # Display character image and details
        st.image(character_details['IMAGE'])
    
    with coln2:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("Gender: ", character_details['GENDER'])
        st.write("Species: ", character_details['SPECIES'], f"({character_details['CHAR_TYPE']})" if character_details['CHAR_TYPE'] else "")
        st.write("Status: ", character_details['STATUS'])
        st.write("Origin: ", character_details['ORIGIN'])
        st.write("Location: ", character_details['LOCATION'])

    # Query to get episodes where the character appeared
    episodes_query = f"""
    SELECT EP_NAME, EP_NUM 
    FROM airbyte_database.dbt_schema.int_ram_episodes 
    JOIN airbyte_database.dbt_schema.fact_ram 
        ON int_ram_episodes.EP_ID = fact_ram.EP_ID 
    WHERE CHAR_ID IN 
        (SELECT CHAR_ID FROM airbyte_database.dbt_schema.int_ram_characters WHERE CHAR_NAME = '{character_name}')
    ORDER BY CAST(SUBSTRING(EP_NUM, 2, 2) AS INTEGER), CAST(SUBSTRING(EP_NUM, 5, 2) AS INTEGER);
    """

    episodes_df = pd.read_sql(episodes_query, conn)

    with coln3:
        # Display episodes
        st.subheader("Appearances")
        for index, row in episodes_df.iterrows():
            st.write(f"Episode {row['EP_NUM']}: {row['EP_NAME']}")