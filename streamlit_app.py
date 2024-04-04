import altair as alt
import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import datetime
import pathlib
import run_queries

"""
# Team Stats


"""

### VISUALIZATION
def load_existing_data(fileprefix):
    files = [file for file in pathlib.Path('.').glob(f"{fileprefix}_*.csv")]
    if len(files) == 0:
        return None
    files.sort()
    latest_file = files[-1]
    latest_date = datetime.datetime.strptime("_".join(files[-1].stem.split('_')[1:]), "%Y-%m-%d_%H-%M-%S")
    return pd.read_csv(latest_file), latest_date

def save_data(date, data, fileprefix):
   data.to_csv(f'{fileprefix}_{date.strftime("%Y-%m-%d_%H-%M-%S")}.csv')

def regenerate_data():
    st.session_state.data_update_date = datetime.datetime.now()
    # Regenerate ticket data
    tickets_df = run_queries.generate_ticket_df()
    save_data(st.session_state.data_update_date, tickets_df, 'tickets')
    st.session_state.ticket_source_df = tickets_df

    prs_df, pr_reviews_df = run_queries.generate_prs_df()
    save_data(st.session_state.data_update_date, prs_df, 'prs')
    save_data(st.session_state.data_update_date, pr_reviews_df, 'prreviews')
    st.session_state.prs_source_df = prs_df
    st.session_state.pr_reviews_source_df = pr_reviews_df

if 'data_update_date' not in st.session_state:
    latest_ticket_data, latest_date = load_existing_data('tickets')
    st.session_state.ticket_source_df = latest_ticket_data
    st.session_state.data_update_date = latest_date
    latest_pr_data, latest_date = load_existing_data('prs')
    st.session_state.prs_source_df = latest_pr_data
    latest_pr_reviews_data, latest_date = load_existing_data('prreviews')
    st.session_state.pr_reviews_source_df = latest_pr_reviews_data
    

col1, col2 = st.columns((2,7))
reload_button = col1.button("Regenerate data", on_click=regenerate_data)
col2.text(f"Last update of data {st.session_state.data_update_date}")


def create_common_chart(source, x,y, title):
    line = alt.Chart(source).mark_line().encode(
        x=x,
        y=f'mean({y}):Q',
        color='variable',
    )
    band = alt.Chart(source).mark_errorband().encode(
        x=x,
        y=y,
        color='variable'
    )
    chart = (line+band).properties(
        title=title,
        width=1300
    ).interactive()
    return chart

def create_individual_chart(source, x,facet, y):
    line2 = alt.Chart(source).mark_line().encode(
        x=x,
        y=y,
        color='variable',
    )
    band2 = alt.Chart(source).mark_errorband().encode(
        x=x,
        y=y,
        color='variable'
    )
    chart2 = (line2+band2).properties(
        width=1000,
        #height=200,
        #title=title,
    ).facet(
        row=f'{facet}:N'
    #).resolve_scale(x='independent'
    ).interactive()
    return chart2

indv_ticket_chart = create_individual_chart(st.session_state.ticket_source_df, 
                                            'closedAt_Friday',
                                            'content_assignees_nodes_login', 
                                            'value')
inv_pr_chart = create_individual_chart(st.session_state.prs_source_df,
                                        'closedAt_Friday',
                                        'author_login',
                                        'value')
inv_pr_review_chart = create_individual_chart(st.session_state.pr_reviews_source_df,
                                            'createdAt_Friday',
                                            'reviews_nodes_author_login',
                                            'value')

common_ticket_chart = create_common_chart(st.session_state.ticket_source_df, 'closedAt_Friday', 'value', 'Team average')
common_pr_chart = create_common_chart(st.session_state.prs_source_df, 'closedAt_Friday', 'value', 'Team average')
common_pr_review_chart = create_common_chart(st.session_state.pr_reviews_source_df, 'createdAt_Friday', 'value', 'Team average')


tab1, tab2, tab3, tab4 = st.tabs(["Tickets", "PRs", "PR Reviews", "Commits"])

with tab1:
   st.header("Tickets")
   st.altair_chart(common_ticket_chart, theme="streamlit", use_container_width=False)
   st.altair_chart(indv_ticket_chart, theme='streamlit', use_container_width=False)

with tab2:
   st.header("PRs")
   st.altair_chart(common_pr_chart, theme='streamlit', use_container_width=False)
   st.altair_chart(inv_pr_chart, theme='streamlit', use_container_width=False)

with tab3:
    st.header("PR Reviews")
    st.altair_chart(common_pr_review_chart, theme='streamlit', use_container_width=False)
    st.altair_chart(inv_pr_review_chart, theme='streamlit', use_container_width=False)

with tab4:
   st.header("Commits")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

