import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Frammer AI Optimization Dashboard",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Frammer AI – Optimization Effectiveness Dashboard")
st.caption("Client: CLIENT 1 | Mar 2025 – Feb 2026")

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------

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

# -------------------------------------------------------
# HELPER
# -------------------------------------------------------

def parse_duration(d):

    if pd.isna(d):
        return 0

    h, m, s = map(int, d.split(":"))
    return h*3600 + m*60 + s


# -------------------------------------------------------
# GLOBAL KPIs
# -------------------------------------------------------

total_uploaded = df_channel["Uploaded Count"].sum()
total_created = df_channel["Created Count"].sum()
total_published = df_channel["Published Count"].sum()

creation_multiplier = round(total_created / total_uploaded,2)

publish_conversion = round((total_published/total_created)*100,2)

waste_rate = round(((total_created-total_published)/total_created)*100,2)

created_sec = df_channel["Created Duration (hh:mm:ss)"].apply(parse_duration).sum()
published_sec = df_channel["Published Duration (hh:mm:ss)"].apply(parse_duration).sum()

duration_waste = round(((created_sec-published_sec)/created_sec)*100,2)

channel_adoption = round(
    (len(df_channel[df_channel["Published Count"]>0])/len(df_channel))*100,2
)

user_adoption = round(
    (len(df_user[df_user["Published Count"]>0])/len(df_user))*100,2
)

# -------------------------------------------------------
# PLATFORM SHARE
# -------------------------------------------------------

platform = df_platform.melt(
    id_vars=["Channels"],
    var_name="Platform",
    value_name="Published"
)

platform_share = platform.groupby("Platform")["Published"].sum().reset_index()

# -------------------------------------------------------
# MONTHLY CONVERSION
# -------------------------------------------------------

df_month["Publish Conversion %"] = (
    df_month["Total Published"] /
    df_month["Total Created"] * 100
).round(2)

# -------------------------------------------------------
# TABS
# -------------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Overview",
    "Creation Analytics",
    "Publishing Performance",
    "Waste Analysis",
    "Data Explorer"
])

# -------------------------------------------------------
# TAB 1 – EXECUTIVE
# -------------------------------------------------------

with tab1:

    st.subheader("Optimization Health KPIs")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Creation Multiplier",f"{creation_multiplier}×")
    c2.metric("Publish Conversion",f"{publish_conversion}%")
    c3.metric("Content Waste",f"{waste_rate}%")
    c4.metric("Duration Waste",f"{duration_waste}%")

    st.divider()

    c5,c6 = st.columns(2)

    c5.metric("Channel Adoption",f"{channel_adoption}%")
    c6.metric("User Publishing Participation",f"{user_adoption}%")

    st.divider()

    st.subheader("Content Optimization Funnel")

    funnel = pd.DataFrame({
        "Stage":["Uploaded","Created","Published"],
        "Count":[total_uploaded,total_created,total_published]
    })

    fig = px.funnel(
        funnel,
        x="Count",
        y="Stage",
        color="Stage"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.info(
        "The AI system generates **3.35× more assets than uploads**, "
        "but less than **1% reach publishing**, indicating strong editorial filtering."
    )

# -------------------------------------------------------
# TAB 2 – CREATION
# -------------------------------------------------------

with tab2:

    st.subheader("Content Creation Distribution")

    fig_input = px.bar(
        df_input.sort_values("Created Count",ascending=False),
        x="Input Type",
        y="Created Count",
        color="Created Count"
    )

    st.plotly_chart(fig_input,use_container_width=True)

    st.subheader("Monthly Creation Trend")

    fig_month = px.line(
        df_month,
        x="Month",
        y=["Total Uploaded","Total Created"],
        markers=True
    )

    st.plotly_chart(fig_month,use_container_width=True)

    st.subheader("User Creation Productivity")

    df_user["Productivity"] = (
        df_user["Created Count"]/df_user["Uploaded Count"]
    ).round(2)

    st.dataframe(
        df_user.sort_values("Productivity",ascending=False)
        .head(10)[["User","Productivity"]],
        use_container_width=True
    )

# -------------------------------------------------------
# TAB 3 – PUBLISHING
# -------------------------------------------------------

with tab3:

    st.subheader("Publish Conversion")

    fig_output = px.bar(
        df_output.sort_values("Published Count",ascending=False),
        x="Output Type",
        y="Published Count",
        color="Published Count"
    )

    st.plotly_chart(fig_output,use_container_width=True)

    st.subheader("Platform Distribution")

    fig_platform = px.pie(
        platform_share,
        names="Platform",
        values="Published",
        hole=0.4
    )

    st.plotly_chart(fig_platform,use_container_width=True)

    st.subheader("Monthly Publish Conversion")

    fig_conv = px.line(
        df_month,
        x="Month",
        y="Publish Conversion %",
        markers=True
    )

    st.plotly_chart(fig_conv,use_container_width=True)

# -------------------------------------------------------
# TAB 4 – WASTE
# -------------------------------------------------------

with tab4:

    st.subheader("Content Waste Analysis")

    df_input["Waste"] = (
        df_input["Created Count"]-
        df_input["Published Count"]
    )

    df_channel["Waste"] = (
        df_channel["Created Count"]-
        df_channel["Published Count"]
    )

    c1,c2 = st.columns(2)

    fig_waste_input = px.bar(
        df_input.nlargest(5,"Waste"),
        x="Waste",
        y="Input Type",
        orientation="h",
        color="Waste"
    )

    c1.plotly_chart(fig_waste_input,use_container_width=True)

    fig_waste_channel = px.bar(
        df_channel.nlargest(5,"Waste"),
        x="Waste",
        y="Channel",
        orientation="h",
        color="Waste"
    )

    c2.plotly_chart(fig_waste_channel,use_container_width=True)

# -------------------------------------------------------
# TAB 5 – EXPLORER
# -------------------------------------------------------

with tab5:

    st.subheader("Channel Leaderboard")

    leaderboard = df_channel.copy()

    leaderboard["Optimization %"] = (
        leaderboard["Published Count"] /
        leaderboard["Created Count"] * 100
    ).round(2)

    leaderboard = leaderboard.sort_values(
        "Optimization %",
        ascending=False
    )

    leaderboard["Rank"] = range(1,len(leaderboard)+1)

    st.dataframe(
        leaderboard[
            ["Rank","Channel","Optimization %","Created Count","Published Count"]
        ],
        use_container_width=True
    )

    st.subheader("Video Explorer")

    query = st.text_input("Search video")

    if query:

        result = df_video[
            df_video["Headline"].str.contains(query,case=False,na=False)
            |
            df_video["Video ID"].astype(str).str.contains(query)
        ]

    else:
        result = df_video.head(500)

    st.dataframe(
        result[
            ["Headline","Type","Uploaded By","Published","Published Platform"]
        ],
        use_container_width=True
    )

st.caption("Frammer AI Championship | AI-Assisted Optimization Analytics")
