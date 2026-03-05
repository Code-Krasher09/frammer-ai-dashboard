import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Frammer AI – Optimization Dashboard",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 Frammer AI – AI Optimization Effectiveness Dashboard")
st.caption("CLIENT 1 | Mar 2025 – Feb 2026")

# =========================================================
# LOAD DATA
# =========================================================

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

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def parse_duration_to_seconds(duration):

    if pd.isna(duration):
        return 0

    h, m, s = map(int, duration.split(":"))
    return h * 3600 + m * 60 + s


# =========================================================
# GLOBAL METRICS
# =========================================================

total_uploaded = df_channel["Uploaded Count"].sum()
total_created = df_channel["Created Count"].sum()
total_published = df_channel["Published Count"].sum()

creation_multiplier = round(total_created / total_uploaded, 2)

publish_conversion = round((total_published / total_created) * 100, 2)

waste_rate = round(((total_created - total_published) / total_created) * 100, 2)

# Duration calculations

created_sec = df_channel["Created Duration (hh:mm:ss)"].apply(parse_duration_to_seconds).sum()
published_sec = df_channel["Published Duration (hh:mm:ss)"].apply(parse_duration_to_seconds).sum()

duration_waste = round(((created_sec - published_sec) / created_sec) * 100, 2)

# Adoption

channel_adoption = round((len(df_channel[df_channel["Published Count"] > 0]) / len(df_channel)) * 100, 2)

user_adoption = round((len(df_user[df_user["Published Count"] > 0]) / len(df_user)) * 100, 2)

# =========================================================
# PLATFORM SHARE
# =========================================================

platform_melt = df_platform.melt(
    id_vars=["Channels"],
    var_name="Platform",
    value_name="Published"
)

platform_share = (
    platform_melt.groupby("Platform")["Published"]
    .sum()
    .reset_index()
)

# =========================================================
# MONTHLY CONVERSION
# =========================================================

df_month["Publish Conversion %"] = (
    df_month["Total Published"] /
    df_month["Total Created"] * 100
).round(2)

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([

    "Executive Summary",
    "Creation & Ingestion",
    "Publish Conversion",
    "Waste & Leakage",
    "Explorer"

])

# =========================================================
# TAB 1 – EXECUTIVE SUMMARY
# =========================================================

with tab1:

    st.subheader("AI Optimization Health")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Creation Multiplier",
        f"{creation_multiplier}×",
        "Assets per upload"
    )

    col2.metric(
        "Publish Conversion",
        f"{publish_conversion}%",
        "Created → Published"
    )

    col3.metric(
        "Content Waste",
        f"{waste_rate}%"
    )

    col4.metric(
        "Duration Waste",
        f"{duration_waste}%"
    )

    st.divider()

    col5, col6 = st.columns(2)

    col5.metric(
        "Channel Adoption",
        f"{channel_adoption}%"
    )

    col6.metric(
        "User Publishing Participation",
        f"{user_adoption}%"
    )

    st.divider()

    st.subheader("Optimization Funnel")

    funnel = pd.DataFrame({

        "Stage": ["Uploaded", "Created", "Published"],
        "Count": [total_uploaded, total_created, total_published]

    })

    fig = px.funnel(
        funnel,
        x="Count",
        y="Stage"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "AI generates **3.35× more assets than uploads**, "
        "but **<1% are published**, indicating strong editorial filtering."
    )

# =========================================================
# TAB 2 – CREATION
# =========================================================

with tab2:

    st.subheader("Content Creation Analysis")

    col1, col2 = st.columns(2)

    fig_input = px.bar(
        df_input.sort_values("Created Count", ascending=False),
        x="Input Type",
        y="Created Count",
        title="Created Assets by Input Type"
    )

    col1.plotly_chart(fig_input, use_container_width=True)

    fig_month = px.line(
        df_month,
        x="Month",
        y=["Total Uploaded", "Total Created"],
        title="Monthly Creation Trend"
    )

    col2.plotly_chart(fig_month, use_container_width=True)

    st.subheader("User Creation Productivity")

    df_user["Productivity"] = (
        df_user["Created Count"] /
        df_user["Uploaded Count"]
    ).round(2)

    st.dataframe(
        df_user.sort_values("Productivity", ascending=False)
        .head(10)[["User", "Productivity"]],
        use_container_width=True
    )

# =========================================================
# TAB 3 – PUBLISH CONVERSION
# =========================================================

with tab3:

    st.subheader("Publish Conversion")

    st.metric(
        "Overall Publish Conversion",
        f"{publish_conversion}%"
    )

    col1, col2 = st.columns(2)

    fig_output = px.bar(
        df_output.sort_values("Published Count", ascending=False),
        x="Output Type",
        y="Published Count",
        title="Published by Output Type"
    )

    col1.plotly_chart(fig_output, use_container_width=True)

    fig_platform = px.pie(
        platform_share,
        names="Platform",
        values="Published",
        hole=0.4,
        title="Platform Distribution"
    )

    col2.plotly_chart(fig_platform, use_container_width=True)

    st.subheader("Monthly Publish Conversion")

    fig_month_conv = px.line(
        df_month,
        x="Month",
        y="Publish Conversion %",
        markers=True
    )

    st.plotly_chart(fig_month_conv, use_container_width=True)

# =========================================================
# TAB 4 – WASTE ANALYSIS
# =========================================================

with tab4:

    st.subheader("Waste Analysis")

    df_input["Waste Index"] = (
        df_input["Created Count"] -
        df_input["Published Count"]
    )

    df_channel["Waste Index"] = (
        df_channel["Created Count"] -
        df_channel["Published Count"]
    )

    col1, col2 = st.columns(2)

    fig_waste_input = px.bar(

        df_input.nlargest(5, "Waste Index"),
        y="Input Type",
        x="Waste Index",
        orientation="h",
        title="Top Waste Generating Formats",
        color="Waste Index",
        color_continuous_scale="reds"

    )

    col1.plotly_chart(fig_waste_input, use_container_width=True)

    fig_waste_channel = px.bar(

        df_channel.nlargest(5, "Waste Index"),
        y="Channel",
        x="Waste Index",
        orientation="h",
        title="Top Waste Channels",
        color="Waste Index",
        color_continuous_scale="reds"

    )

    col2.plotly_chart(fig_waste_channel, use_container_width=True)

    st.metric(
        "Total Wasted Assets",
        f"{total_created-total_published:,}"
    )

    st.metric(
        "Wasted Duration (hours)",
        f"{(created_sec-published_sec)/3600:.1f}"
    )

# =========================================================
# TAB 5 – DATA EXPLORER
# =========================================================

with tab5:

    st.subheader("Channel Leaderboard")

    leaderboard = df_channel.copy()

    leaderboard["Optimization Score %"] = (
        leaderboard["Published Count"] /
        leaderboard["Created Count"] * 100
    ).round(2)

    leaderboard = leaderboard.sort_values(
        "Optimization Score %",
        ascending=False
    )

    leaderboard["Rank"] = range(1, len(leaderboard)+1)

    st.dataframe(

        leaderboard[
            ["Rank", "Channel", "Optimization Score %", "Created Count", "Published Count"]
        ],

        use_container_width=True

    )

    st.subheader("Video Explorer")

    search = st.text_input("Search by headline or video ID")

    if search:

        results = df_video[
            df_video["Headline"].str.contains(search, case=False, na=False)
            |
            df_video["Video ID"].astype(str).str.contains(search)
        ]

    else:

        results = df_video.head(500)

    st.dataframe(
        results[
            ["Headline", "Type", "Uploaded By", "Published", "Published Platform"]
        ],
        use_container_width=True
    )

    st.subheader("Natural Language Demo")

    query = st.text_input("Ask something about the data")

    if query:

        q = query.lower()

        if "best channel" in q:

            best = leaderboard.iloc[0]

            st.success(
                f"Best channel is **{best['Channel']}** "
                f"with {best['Optimization Score %']}% publish rate."
            )

        elif "waste" in q:

            worst = df_input.nlargest(1, "Waste Index").iloc[0]

            st.success(
                f"Most waste occurs in **{worst['Input Type']}** "
                f"with {worst['Waste Index']} unused assets."
            )

        else:

            st.info("Try queries like 'best channel' or 'waste formats'.")

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Frammer AI Championship | KPI Framework based on Optimization Efficiency"
)
