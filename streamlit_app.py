# Import python packages
import streamlit as st
import requests
import pandas as pd
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col


# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """ Choose the fruits you want in your custom smoothie
    """
)


name_on_order = st.text_input("Name on your smoothie")
st.write("The name on your smoothie will be: ", name_on_order)

# session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col("SEARCH_ON"))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

ingredients_list = st.multiselect("Choose up to 5 ingredients: ", my_dataframe, max_selections = 5)

if ingredients_list:

    ingredients_string = ""
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        # st.text(smoothiefroot_response)
        sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width = True)
    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    # time_to_insert = st.button("Submit Order")
    
    # if time_to_insert:
    #     session.sql(my_insert_stmt).collect()
    #     st.success('Your Smoothie is ordered! ' + name_on_order, icon="✅")


    my_order = """ select order_uid as order_id from smoothies.public.orders order by order_ts desc limit 1 """
    # st.write(my_insert_stmt)
    # st.stop()
    time_to_insert = st.button("Submit Order")
    
    if time_to_insert:
        for fruit_chosen in ingredients_list:
            my_update_stmt = """UPDATE smoothies.public.fruit_options SET quantity = quantity - 1 WHERE fruit_name = '""" + fruit_chosen + """';""" 
            session.sql(my_insert_stmt).collect()
            st.write(my_update_stmt)
        # st.stop()
        session.sql(my_update_stmt).collect()
        order_submitted = session.sql(my_order).collect()
        st.success('Hi '+ name_on_order + ', Your ' + str(order_submitted[0]) + ' has been submitted', icon="✅")
