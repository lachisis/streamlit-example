import altair as alt
import streamlit as st
st.set_page_config(layout="wide")

import datetime
import utils
import run_queries
import utils_df

"""
# Team Stats


"""
DEBUG=False

### VISUALIZATION
def regenerate_data():
    st.session_state.data_update_date = datetime.datetime.now()
    # Regenerate ticket data
    github_items, github_fields = run_queries.regenerate_ticket_data(st.session_state.data_update_date)
    github_prs = run_queries.regenerate_prs_data(st.session_state.data_update_date)
    return github_items, github_fields, github_prs


if 'data_update_date' not in st.session_state:
    #regenerate_data()
    # This is the first load of the app, load old data so we don't call regenerate every time
    github_items, latest_date = utils.load_existing_data('github_items', 'json')
    github_fields, latest_date = utils.load_existing_data('github_fields', 'json')
    github_prs, latest_date = utils.load_existing_data('github_prs', 'json')

    st.session_state.data_update_date = latest_date
    st.session_state.github_items = github_items
    st.session_state.github_fields = github_fields
    st.session_state.github_prs = github_prs
 

tickets_df_raw, tickets_df_melted = utils_df.generate_ticket_df(st.session_state.github_items, st.session_state.github_fields)
print(tickets_df_raw)
print(tickets_df_melted)

prs_df_raw, prs_df, pr_reviews_df_raw, pr_reviews_df = utils_df.format_prs_df(st.session_state.github_prs)
print(prs_df.head())
print(pr_reviews_df.head())

col1, col2 = st.columns((2,7))
reload_button = col1.button("Regenerate data", on_click=regenerate_data)
col2.text(f"Last update of data {st.session_state.data_update_date}")

def create_common_chart_ind(source, x,y, title, color, variable="size_all"): 
    selection = alt.selection_multi(fields=[color], bind='legend')
    selection2 = alt.selection_multi(fields=['variable'], bind='legend')
    #source = source[source['variable'] == 'size_all']
    lines = alt.Chart(source).mark_line().encode(
        x=x,
        y=y,
        color=color,
        strokeDash='variable',
        opacity=alt.condition(selection & selection2, alt.value(1), alt.value(0.1))
    )
    lines2 = alt.Chart(source).mark_line().encode(
        x=x,
        y=f'mean({y}):Q',
        color=alt.value('#000000'),
        strokeDash='variable',
        opacity=alt.condition(selection2, alt.value(1), alt.value(0.1))
    )
    band = alt.Chart(source[source['variable'] == variable]).mark_errorband().encode(
        x=x,
        y=y,
        color=alt.value("#000000"),
        strokeDash='variable',
        opacity=alt.condition(selection2, alt.value(0.1), alt.value(0.0))
    ) 
    chart = (lines+lines2+band).properties(
        title=title,
    ).add_params(selection).add_params(selection2).interactive()
    return chart

def create_common_chart_sum(source, x,y, title):
    line = alt.Chart(source).mark_line().encode(
        x=x,
        y=f'sum({y}):Q',
        color='variable',
    )
    chart = (line).properties(
        title=title,
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

    ).facet(
        row=f'{facet}:N'
    ).interactive()
    return chart2

indv_ticket_chart = create_individual_chart(tickets_df_melted, 
                                            'closedAt_Friday',
                                            'assignee', 
                                            'value')
inv_pr_chart = create_individual_chart(prs_df,
                                        'closedAt_Friday',
                                        'author_login',
                                        'value')
inv_pr_review_chart = create_individual_chart(pr_reviews_df,
                                            'createdAt_Friday',
                                            'reviews_nodes_author_login',
                                            'value')

common_ticket_chart_ind = create_common_chart_ind(tickets_df_melted, 'closedAt_Friday', 'value', 'Team average',
    color='assignee', variable="size_all")
common_ticket_chart = create_common_chart_sum(tickets_df_melted, 'closedAt_Friday', 'value', 'Team sum')
common_pr_chart = create_common_chart_sum(prs_df, 'closedAt_Friday', 'value', 'Team sum')
common_pr_chart_ind = create_common_chart_ind(prs_df, 'closedAt_Friday', 'value', 'Team average',
                                              color='author_login', variable="closed")
common_pr_review_chart = create_common_chart_sum(pr_reviews_df, 'createdAt_Friday', 'value', 'Team sum')
common_pr_review_chart_ind = create_common_chart_ind(pr_reviews_df, 'createdAt_Friday', 'value', 'Team average',
                                                     color='author', variable="created")


tab1, tab2, tab3, tab4 = st.tabs(["Tickets", "PRs", "PR Reviews", "Commits"])

with tab1:
    st.header("Tickets")
    st.altair_chart(common_ticket_chart, theme="streamlit", use_container_width=True)  
    st.altair_chart(common_ticket_chart_ind, theme="streamlit", use_container_width=True)
    st.dataframe(utils_df.build_table(tickets_df_raw, 'closedAt_Friday', 'assignee', 'size_all').round(1))

with tab2:
   st.header("PRs")
   st.altair_chart(common_pr_chart, theme="streamlit", use_container_width=True)  
   st.altair_chart(common_pr_chart_ind, theme='streamlit', use_container_width=True)
   st.dataframe(utils_df.build_table(prs_df_raw, 'closedAt_Friday', 'author_login', 'closed').round(1))

with tab3:
    st.header("PR Reviews")
    st.altair_chart(common_pr_review_chart, theme='streamlit', use_container_width=True)
    st.altair_chart(common_pr_review_chart_ind, theme='streamlit', use_container_width=True)
    st.dataframe(utils_df.build_table(pr_reviews_df_raw, 'createdAt_Friday', 'author', 'created').round(1))

with tab4:
   st.header("Commits")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
