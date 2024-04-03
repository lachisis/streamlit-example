import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

"""
# Team Stats


"""

source = pd.read_csv('tmp.csv')

line = alt.Chart(source).mark_line().encode(
    x='closedAt_Friday',
    y='mean(value):Q',
    color='variable',
)
band = alt.Chart(source).mark_errorband().encode(
    x='closedAt_Friday',
    y='value',
    color='variable'
)
chart = (line+band).properties(
    title='Team average'
).interactive()

line2 = alt.Chart(source).mark_line().encode(
    x='closedAt_Friday',
    y='value',
    color='variable',
)
band2 = alt.Chart(source).mark_errorband().encode(
    x='closedAt_Friday',
    y='value',
    color='variable'
)
chart2 = (line2+band2).properties(
    width=400,
    height=200,
).facet(
    row='content_assignees_nodes_login:N'
)


# chart2 = alt.vconcat()
# for user in list(source['content_assignees_nodes_login'].unique()):
#     chart2 &= base2.transform_filter(alt.datum.content_assignees_nodes_login == user)
# chart2 = chart2.interactive()

# chart = alt.vconcat(data=iris)
# for y_encoding in ['petalLength:Q', 'petalWidth:Q']:
#     row = alt.hconcat()
#     for x_encoding in ['sepalLength:Q', 'sepalWidth:Q']:
#         row |= base.encode(x=x_encoding, y=y_encoding)
#     chart &= row
# chart

### VISUALIZATION

tab1, tab2, tab3 = st.tabs(["Tickets", "PRs", "Commits"])

with tab1:
   st.header("Tickets")
   st.altair_chart(chart, theme="streamlit", use_container_width=True)
   st.altair_chart(chart2, theme='streamlit', use_container_width=True)

with tab2:
   st.header("PRs")
   st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

with tab3:
   st.header("Commits")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

num_points = st.slider("Number of points in spiral", 1, 10000, 1100)
num_turns = st.slider("Number of turns in spiral", 1, 300, 31)

indices = np.linspace(0, 1, num_points)
theta = 2 * np.pi * num_turns * indices
radius = indices

x = radius * np.cos(theta)
y = radius * np.sin(theta)

df = pd.DataFrame({
    "x": x,
    "y": y,
    "idx": indices,
    "rand": np.random.randn(num_points),
})

st.altair_chart(alt.Chart(df, height=700, width=700)
    .mark_point(filled=True)
    .encode(
        x=alt.X("x", axis=None),
        y=alt.Y("y", axis=None),
        color=alt.Color("idx", legend=None, scale=alt.Scale()),
        size=alt.Size("rand", legend=None, scale=alt.Scale(range=[1, 150])),
    ))
