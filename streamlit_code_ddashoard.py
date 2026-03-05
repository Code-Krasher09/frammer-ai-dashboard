import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Frammer AI - AI Optimization Effectiveness",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Frammer AI – AI Optimization Effectiveness Dashboard")
st.markdown("**CLIENT 1 (Mar 2025 – Feb 2026)** | Turning 3.35× content creation into audience impact")

# ====================== LOAD DATA ======================
@st.cache_data
def load_data():
    try:
        df_input = pd.read_csv("combined_data(2025-3-1-2026-2-28) by input type.csv")
        df_output = pd.read_csv("combined_data(2025-3-1-2026-2-28) by output type.csv")
        df_channel = pd.read_csv("CLIENT 1 combined_data(2025-3-1-2026-2-28).csv")
        df_user = pd.read_csv("combined_data(2025-3-1-2026-2-28) by user.csv")
        df_month = pd.read_csv("monthly-chart.csv")
        df_platform = pd.read_csv("channel-wise-publishing.csv")
        df_video = pd.read_csv("video_list_data_obfuscated.csv")
        return df_input, df_output, df_channel, df_user, df_month, df_platform, df_video
    except FileNotFoundError as e:
        st.error(f"Missing CSV file: {e}. Please ensure all data files are in the same directory.")
        st.stop()

df_input, df_output, df_channel, df_user, df_month, df_platform, df_video = load_data()

# ====================== PRE-COMPUTED METRICS (Strategic + Supporting KPIs) ======================
total_uploaded = df_channel["Uploaded Count"].sum()
total_created = df_channel["Created Count"].sum()
total_published = df_channel["Published Count"].sum()

# Strategic KPIs
ai_creation_mult = round((total_created / total_uploaded) * 100, 2)
ai_publish_conv = round((total_published / total_created) * 100, 2)
ai_waste_count = round(((total_created - total_published) / total_created) * 100, 2)

# Duration-based (parse hh:mm:ss to seconds for accuracy)
def parse_duration_to_seconds(duration_str):
    if pd.isna(duration_str):
        return 0
    parts = duration_str.split(':')
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

total_created_sec = sum(parse_duration_to_seconds(d) for d in df_channel["Created Duration (hh:mm:ss)"])
total_published_sec = sum(parse_duration_to_seconds(d) for d in df_channel["Published Duration (hh:mm:ss)"])
ai_waste_duration = round(((total_created_sec - total_published_sec) / total_created_sec) * 100, 2) if total_created_sec > 0 else 0

channel_adoption = round((len(df_channel[df_channel['Published Count'] > 0]) / len(df_channel)) * 100, 2)
user_participation = round((len(df_user[df_user['Published Count'] > 0]) / len(df_user)) * 100, 2)
top_contrib_share = 59.70  # From EDA; compute dynamically if needed
input_opt_score = (df_input['Published Count'] / df_input['Created Count'] * 100).round(2)
channel_opt_score = (df_channel['Published Count'] / df_channel['Created Count'] * 100).round(2)

# Platform Share (melt and aggregate)
df_platform_melted = df_platform.melt(id_vars=["Channels"], var_name="Platform", value_name="Published Count")
platform_share = df_platform_melted.groupby("Platform")["Published Count"].sum() / total_published * 100

# Monthly AI Conversion Trend
df_month['Publish Conversion %'] = (df_month['Total Published'] / df_month['Total Created'] * 100).round(2)

# Supporting KPIs
df_input['Waste Index'] = df_input['Created Count'] - df_input['Published Count']
df_channel['Waste Index'] = df_channel['Created Count'] - df_channel['Published Count']
user_opt_eff = (df_user['Published Count'] / df_user['Created Count'] * 100).round(2)
user_creation_prod = (df_user['Created Count'] / df_user['Uploaded Count']).round(2)
duration_opt_eff = round((total_published_sec / total_created_sec) * 100, 2)

# Double-dim examples (simplified; expand with full joins for production)
# Channel-User: Placeholder top from EDA
channel_user_top = pd.DataFrame({
    'Pair': ['A-Harish', 'C-Abhishek', 'B-Adarsh'],
    'Optimization %': [7.3, 6.8, 6.0]
})
# User-Input: Placeholder
user_input_top = pd.DataFrame({
    'Pair': ['Abhishek-News Bulletin', 'Harish-News Bulletin', 'Neha-Special Reports'],
    'Optimization %': [7.0, 5.3, 3.6]
})

# ====================== SIDEBAR FILTERS ======================
st.sidebar.header("Filters")
selected_channels = st.sidebar.multiselect("Channels", df_channel["Channel"].unique(), default=df_channel["Channel"].unique())
date_range = st.sidebar.date_input("Period", [datetime(2025,3,1), datetime(2026,2,28)])

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Summary",
    "Ingestion & Creation",
    "Publish Conversion",
    "Waste & Leakage",
    "Leaderboard & Explorer"
])

# ====================== TAB 1: EXECUTIVE SUMMARY ======================
with tab1:
    st.subheader("Strategic KPIs – AI Optimization Health")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AI Creation Multiplication", f"{ai_creation_mult}% (3.35×)")
    col2.metric("AI Publish Conversion", f"{ai_publish_conv}%", "Alert: <1% threshold")
    col3.metric("AI Waste Rate (Count)", f"{ai_waste_count}%")
    col4.metric("AI Waste Rate (Duration)", f"{ai_waste_duration}%")

    col5, col6, col7 = st.columns(3)
    col5.metric("Channel Optimization Adoption", f"{channel_adoption}%")
    col6.metric("User Optimization Participation", f"{user_participation}%")
    col7.metric("Top Optimizer Dependency", f"{top_contrib_share}%", "Alert: High concentration risk")

    st.subheader("Optimization Funnel")
    funnel_data = pd.DataFrame({
        "Stage": ["Uploaded", "Created", "Published"],
        "Count": [total_uploaded, total_created, total_published]
    })
    fig_funnel = px.funnel(funnel_data, x="Count", y="Stage", title="AI Optimization Funnel")
    st.plotly_chart(fig_funnel, use_container_width=True)

    st.subheader("Top 3 Winners")
    winner1, winner2, winner3 = st.columns(3)
    winner1.metric("Best Channel Score", f"Channel A ({channel_opt_score.iloc[0]}%)", "71 published")
    winner2.metric("Best Input Type Score", f"News Bulletin ({input_opt_score.max()}%)")
    winner3.metric("Best Platform Share", f"YouTube ({platform_share.get('Youtube', 0):.1f}%)")

# ====================== TAB 2: INGESTION & CREATION ======================
with tab2:
    st.subheader("Upload → Created Effectiveness (Supporting KPIs)")
    st.metric("Total Uploaded", f"{total_uploaded:,}")
    st.metric("Total Created by AI", f"{total_created:,} ({ai_creation_mult}% multiplication)")

    col1, col2 = st.columns(2)
    with col1:
        fig_input = px.bar(df_input.sort_values("Created Count", ascending=False).head(8),
                           x="Input Type", y="Created Count", title="Created Assets by Input Type")
        st.plotly_chart(fig_input, use_container_width=True)
    with col2:
        fig_month = px.line(df_month, x="Month", y=["Total Uploaded", "Total Created"],
                            title="Monthly Creation Trend")
        st.plotly_chart(fig_month, use_container_width=True)

    st.subheader("User Creation Productivity (Top 5)")
    user_prod_df = pd.DataFrame({
        'User': df_user['User'].head(5),
        'Productivity': user_creation_prod.head(5)
    })
    st.dataframe(user_prod_df, use_container_width=True)

    st.subheader("Monthly AI Conversion Trend")
    fig_monthly_conv = px.line(df_month, x="Month", y="Publish Conversion %", title="Monthly Publish Conversion %")
    st.plotly_chart(fig_monthly_conv, use_container_width=True)

# ====================== TAB 3: PUBLISH CONVERSION ======================
with tab3:
    st.subheader("Created → Published Conversion (Strategic KPIs)")
    st.metric("Overall AI Publish Conversion", f"{ai_publish_conv}%")

    col1, col2 = st.columns(2)
    with col1:
        fig_output = px.bar(df_output.sort_values("Published Count", ascending=False),
                            x="Output Type", y="Published Count", title="Published by Output Type")
        st.plotly_chart(fig_output, use_container_width=True)
    with col2:
        fig_platform = px.pie(values=platform_share.values, names=platform_share.index,
                              title="Platform Optimization Share %")
        st.plotly_chart(fig_platform, use_container_width=True)

    st.subheader("Input Type Optimization Scores")
    input_scores_df = pd.DataFrame({
        'Input Type': df_input['Input Type'],
        'Optimization Score %': input_opt_score
    }).sort_values('Optimization Score %', ascending=False)
    st.dataframe(input_scores_df.head(10), use_container_width=True)

    st.subheader("Double-Dimension: Channel × Output Type Heatmap")
    # Placeholder heatmap using available data
    heatmap_data = pd.DataFrame({
        "Channel": ["A","B","C","D","E"],
        "Reels": [5,0,0,15,0],
        "Shorts": [1,0,0,18,0],
        "YouTube": [5,0,0,29,0]
    })
    fig_heat = px.imshow(heatmap_data.set_index("Channel").T, text_auto=True, aspect="auto",
                         title="Channel × Output Type Publish Count")
    st.plotly_chart(fig_heat, use_container_width=True)

    st.subheader("Duration Optimization Efficiency")
    st.metric("Published Duration / Created Duration", f"{duration_opt_eff}%")

# ====================== TAB 4: WASTE & LEAKAGE ======================
with tab4:
    st.subheader("Waste & Leakage Intelligence (Supporting KPIs)")
    st.metric("Total Wasted Assets", f"{total_created - total_published:,}")
    st.metric("Total Wasted Hours", f"≈ {(total_created_sec - total_published_sec)/3600:.1f} hrs ({ai_waste_duration}%)")

    col1, col2 = st.columns(2)
    with col1:
        fig_waste_input = px.bar(df_input.nlargest(5, "Waste Index"),
                                 x="Input Type", y="Waste Index", title="Top 5 Input Type Waste Index")
        st.plotly_chart(fig_waste_input, use_container_width=True)
    with col2:
        fig_waste_channel = px.bar(df_channel.nlargest(5, "Waste Index"),
                                   x="Channel", y="Waste Index", title="Top 5 Channel Waste Index")
        st.plotly_chart(fig_waste_channel, use_container_width=True)

    st.subheader("Waste Indices (Top 5 Tables)")
    col_a, col_b = st.columns(2)
    with col_a:
        st.dataframe(df_input.nlargest(5, 'Waste Index')[['Input Type', 'Waste Index']], use_container_width=True)
    with col_b:
        st.dataframe(df_channel.nlargest(5, 'Waste Index')[['Channel', 'Waste Index']], use_container_width=True)

    st.info("**Root Cause Highlight**: 100% waste in Channel D + heavy waste in Interviews/News Bulletins (950+ hrs)")

# ====================== TAB 5: LEADERBOARD & EXPLORER ======================
with tab5:
    st.subheader("Optimization Leaderboard (Strategic KPIs)")
    leaderboard = df_channel[["Channel", "Created Count", "Published Count"]].copy()
    leaderboard["Channel Optimization Score %"] = channel_opt_score
    leaderboard["Waste Index"] = df_channel['Waste Index']
    st.dataframe(leaderboard.sort_values("Channel Optimization Score %", ascending=False), use_container_width=True)

    st.subheader("User Optimization Efficiency (Top 10)")
    user_eff_df = pd.DataFrame({
        'User': df_user['User'],
        'Optimization Efficiency %': user_opt_eff
    }).sort_values('Optimization Efficiency %', ascending=False).head(10)
    st.dataframe(user_eff_df, use_container_width=True)

    st.subheader("Double-Dimension Leaders")
    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("Channel-User Optimization Pairs (Top)")
        st.dataframe(channel_user_top, use_container_width=True)
    with col_d:
        st.subheader("User-Input Optimization Pairs (Top)")
        st.dataframe(user_input_top, use_container_width=True)

    st.subheader("Video Explorer (Searchable Detail Table)")
    search = st.text_input("Search Headline or Video ID")
    if search:
        filtered_video = df_video[df_video["Headline"].str.contains(search, na=False, case=False) |
                                  df_video["Video ID"].astype(str).str.contains(search)]
    else:
        filtered_video = df_video.head(500)
    st.dataframe(filtered_video[["Headline", "Type", "Uploaded By", "Published", "Published Platform"]], use_container_width=True)

    st.subheader("Natural Language Query (Simple Demo)")
    query = st.text_input("Ask anything (e.g., 'Show Channel Optimization Scores' or 'Waste for interviews')")
    if "channel optimization" in query.lower():
        st.success("✅ Filters: All time | Dimension 1 = Channel\n\nChannel A leads at 1.50%. Full table above.")
    elif "waste" in query.lower():
        st.success("✅ Filters: Input Type\n\nTop waste: Interview (4,937 assets). See Waste Tab for details.")
    else:
        st.info("Try: 'Which channel is best?' or 'Show waste for interviews'")

# ====================== FOOTER ======================
st.caption("Built for Frammer AI General Championship 2026 | Data Model: Star Schema | Theme: AI-Assisted Optimizer")
st.caption("KPI Framework: 15 Metrics (Strategic + Supporting) for Scalable Insights")
