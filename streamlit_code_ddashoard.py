import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Frammer AI Optimization Dashboard",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Frammer AI – AI Optimization Effectiveness Dashboard")
st.caption("Client: CLIENT 1 | Mar 2025 – Feb 2026")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

@st.cache_data
def load_data():

    df_input = pd.read_csv("combined_data(2025-3-1-2026-2-28) by input type.csv")
    df_output = pd.read_csv("combined_data(2025-3-1-2026-2-28) by output type.csv")
    df_channel = pd.read_csv("CLIENT 1 combined_data(2025-3-1-2026-2-28).csv")
    df_user = pd.read_csv("combined_data(2025-3-1-2026-2-28) by user.csv")
    df_month = pd.read_csv("monthly-chart.csv")
    df_platform = pd.read_csv("channel-wise-publishing.csv")
    df_video = pd.read_csv("video_list_data_obfuscated.csv")

    return df_input, df_output, df_channel, df_user, df_month, df_platform, df_video


df_input, df_output, df_channel, df_user, df_month, df_platform, df_video = load_data()

# ------------------------------------------------
# CORE METRICS
# ------------------------------------------------

total_uploaded = df_channel["Uploaded Count"].sum()
total_created = df_channel["Created Count"].sum()
total_published = df_channel["Published Count"].sum()

creation_multiplier = round(total_created / total_uploaded,2)
publish_conversion = round((total_published/total_created)*100,2)
end_to_end = round((total_published/total_uploaded)*100,2)

# ------------------------------------------------
# KPI CARDS
# ------------------------------------------------

st.subheader("Core Pipeline KPIs")

c1,c2,c3,c4 = st.columns(4)

c1.metric("Creation Multiplier",f"{creation_multiplier}×")
c2.metric("Publish Conversion",f"{publish_conversion}%")
c3.metric("End-to-End Publish Rate",f"{end_to_end}%")
c4.metric("Total Published",total_published)

st.divider()

# ------------------------------------------------
# FUNNEL VISUAL
# ------------------------------------------------

st.subheader("Content Pipeline Funnel")

funnel = pd.DataFrame({
"Stage":["Uploaded","Created","Published"],
"Count":[total_uploaded,total_created,total_published]
})

fig = px.funnel(funnel,x="Count",y="Stage",color="Stage")

st.plotly_chart(fig,use_container_width=True)

# ------------------------------------------------
# MONTHLY TREND
# ------------------------------------------------

st.subheader("Pipeline Growth Over Time")

fig = px.line(
df_month,
x="Month",
y=["Total Uploaded","Total Created","Total Published"],
markers=True
)

st.plotly_chart(fig,use_container_width=True)

# ------------------------------------------------
# FORMAT PERFORMANCE
# ------------------------------------------------

st.subheader("Format Publish Probability")

df_input["Publish Probability"] = (
df_input["Published Count"]/df_input["Created Count"]
)

fig = px.bar(
df_input.sort_values("Publish Probability",ascending=False),
x="Input Type",
y="Publish Probability",
color="Publish Probability"
)

st.plotly_chart(fig,use_container_width=True)

# ------------------------------------------------
# WASTE ANALYSIS
# ------------------------------------------------

st.subheader("Content Waste Analysis")

df_input["Waste"] = (
df_input["Created Count"] - df_input["Published Count"]
)

fig = px.bar(
df_input.sort_values("Waste",ascending=False).head(10),
y="Input Type",
x="Waste",
orientation="h",
color="Waste"
)

st.plotly_chart(fig,use_container_width=True)

# ------------------------------------------------
# CHANNEL VS PLATFORM HEATMAP
# ------------------------------------------------

st.subheader("Channel × Platform Publishing")

heatmap = df_platform.set_index("Channels")

fig = px.imshow(
heatmap,
text_auto=True,
aspect="auto",
color_continuous_scale="Blues"
)

st.plotly_chart(fig,use_container_width=True)

# ------------------------------------------------
# CHANNEL PERFORMANCE SCATTER
# ------------------------------------------------

st.subheader("Channel Efficiency")

fig = px.scatter(
df_channel,
x="Created Count",
y="Published Count",
size="Uploaded Count",
color="Channel",
hover_name="Channel"
)

st.plotly_chart(fig,use_container_width=True)

# ------------------------------------------------
# PARETO USER CONTRIBUTION
# ------------------------------------------------

st.subheader("Contributor Pareto Distribution")

user_sorted = df_user.sort_values("Created Count",ascending=False)

user_sorted["cum_share"] = user_sorted["Created Count"].cumsum()/user_sorted["Created Count"].sum()

fig = go.Figure()

fig.add_trace(
go.Bar(
x=user_sorted["User"],
y=user_sorted["Created Count"],
name="Created"
)
)

fig.add_trace(
go.Scatter(
x=user_sorted["User"],
y=user_sorted["cum_share"],
name="Cumulative %",
yaxis="y2"
)
)

fig.update_layout(
yaxis2=dict(overlaying="y",side="right",range=[0,1])
)

st.plotly_chart(fig,use_container_width=True)

# ------------------------------------------------
# LORENZ CURVE (CHANNEL INEQUALITY)
# ------------------------------------------------

st.subheader("Publishing Inequality (Lorenz Curve)")

vals = np.sort(df_channel["Published Count"])

cumvals = np.cumsum(vals)/np.sum(vals)

lorenz = np.insert(cumvals,0,0)

x = np.linspace(0,1,len(lorenz))

fig = go.Figure()

fig.add_trace(go.Scatter(x=x,y=lorenz,name="Lorenz Curve"))

fig.add_trace(go.Scatter(x=[0,1],y=[0,1],name="Equality Line"))

st.plotly_chart(fig,use_container_width=True)

# ------------------------------------------------
# VIDEO EXPLORER
# ------------------------------------------------

st.subheader("Video Explorer")

query = st.text_input("Search headline or video id")

if query:

    results = df_video[
        df_video["Headline"].str.contains(query,case=False,na=False) |
        df_video["Video ID"].astype(str).str.contains(query)
    ]

else:

    results = df_video.head(500)

st.dataframe(results)

st.caption("Frammer AI Championship Dashboard – Advanced Visual Analytics")
