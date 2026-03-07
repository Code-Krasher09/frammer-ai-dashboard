import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Frammer AI Optimization Dashboard",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Frammer AI – AI Optimization Effectiveness Dashboard")
st.caption("Client: CLIENT 1 | Mar 2025 – Feb 2026")

# -----------------------------------------------------
# LOAD DATA
# -----------------------------------------------------

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

# -----------------------------------------------------
# HELPER
# -----------------------------------------------------

def parse_duration(d):

    if pd.isna(d):
        return 0

    h, m, s = map(int, d.split(":"))
    return h*3600 + m*60 + s


# -----------------------------------------------------
# CORE METRICS
# -----------------------------------------------------

total_uploaded = df_channel["Uploaded Count"].sum()
total_created = df_channel["Created Count"].sum()
total_published = df_channel["Published Count"].sum()

creation_multiplier = round(total_created / total_uploaded,2)

publish_conversion = round((total_published/total_created)*100,2)

end_to_end_publish = round((total_published/total_uploaded)*100,2)

waste_rate = round(((total_created-total_published)/total_created)*100,2)

# duration metrics
created_sec = df_channel["Created Duration (hh:mm:ss)"].apply(parse_duration).sum()
published_sec = df_channel["Published Duration (hh:mm:ss)"].apply(parse_duration).sum()

duration_efficiency = round((published_sec/created_sec)*100,2)
duration_waste = round(((created_sec-published_sec)/created_sec)*100,2)

# adoption
channel_adoption = round(
    (len(df_channel[df_channel["Published Count"]>0])/len(df_channel))*100,2
)

user_adoption = round(
    (len(df_user[df_user["Published Count"]>0])/len(df_user))*100,2
)

# -----------------------------------------------------
# PLATFORM SHARE
# -----------------------------------------------------

platform = df_platform.melt(
    id_vars=["Channels"],
    var_name="Platform",
    value_name="Published"
)

platform_share = platform.groupby("Platform")["Published"].sum().reset_index()

# -----------------------------------------------------
# MONTHLY CONVERSION
# -----------------------------------------------------

df_month["Publish Conversion %"] = (
    df_month["Total Published"] /
    df_month["Total Created"] * 100
).round(2)

# -----------------------------------------------------
# ADVANCED KPIs
# -----------------------------------------------------

# 1️⃣ Publish Entropy
publish_dist = df_input["Published Count"] / df_input["Published Count"].sum()
publish_entropy = -np.sum(publish_dist * np.log(publish_dist + 1e-9))

# 2️⃣ KL Divergence
created_dist = df_input["Created Count"] / df_input["Created Count"].sum()

kl_divergence = np.sum(
    publish_dist * np.log((publish_dist + 1e-9)/(created_dist + 1e-9))
)

# 3️⃣ Channel Gini Index

channel_values = df_channel["Published Count"].values
channel_values = np.sort(channel_values)

n = len(channel_values)

gini = (
    (2*np.sum((np.arange(1,n+1))*channel_values)) /
    (n*np.sum(channel_values)+1e-9)
) - (n+1)/n

# 4️⃣ Publishing Consistency Score

publish_std = np.std(df_month["Publish Conversion %"])
consistency_score = round(1/(publish_std+1e-5),2)

# -----------------------------------------------------
# TABS
# -----------------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Executive Overview",
    "Creation Analytics",
    "Publishing Performance",
    "Waste Analysis",
    "Team Insights",
    "Advanced Analytics"
])

# -----------------------------------------------------
# TAB 1 EXECUTIVE
# -----------------------------------------------------

with tab1:

    st.subheader("Core Performance KPIs")

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric("Creation Multiplier",f"{creation_multiplier}×")
    c2.metric("Publish Conversion",f"{publish_conversion}%")
    c3.metric("End-to-End Publish Rate",f"{end_to_end_publish}%")
    c4.metric("Processing Efficiency",f"{duration_efficiency}%")
    c5.metric("Waste Rate",f"{waste_rate}%")

    st.divider()

    st.subheader("Optimization Funnel")

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

# -----------------------------------------------------
# TAB 2 CREATION
# -----------------------------------------------------

with tab2:

    fig_input = px.bar(
        df_input.sort_values("Created Count",ascending=False),
        x="Input Type",
        y="Created Count",
        color="Created Count"
    )

    st.plotly_chart(fig_input,use_container_width=True)

    fig_month = px.line(
        df_month,
        x="Month",
        y=["Total Uploaded","Total Created"],
        markers=True
    )

    st.plotly_chart(fig_month,use_container_width=True)

# -----------------------------------------------------
# TAB 3 PUBLISHING
# -----------------------------------------------------

with tab3:

    fig_output = px.bar(
        df_output.sort_values("Published Count",ascending=False),
        x="Output Type",
        y="Published Count",
        color="Published Count"
    )

    st.plotly_chart(fig_output,use_container_width=True)

    fig_platform = px.pie(
        platform_share,
        names="Platform",
        values="Published",
        hole=0.4
    )

    st.plotly_chart(fig_platform,use_container_width=True)

    fig_conv = px.line(
        df_month,
        x="Month",
        y="Publish Conversion %",
        markers=True
    )

    st.plotly_chart(fig_conv,use_container_width=True)

# -----------------------------------------------------
# TAB 4 WASTE
# -----------------------------------------------------

with tab4:

    df_input["Waste"] = (
        df_input["Created Count"]-
        df_input["Published Count"]
    )

    fig_waste = px.bar(
        df_input.nlargest(5,"Waste"),
        y="Input Type",
        x="Waste",
        orientation="h",
        color="Waste"
    )

    st.plotly_chart(fig_waste,use_container_width=True)

# -----------------------------------------------------
# TAB 5 TEAM
# -----------------------------------------------------

with tab5:

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

# -----------------------------------------------------
# TAB 6 ADVANCED ANALYTICS
# -----------------------------------------------------

with tab6:

    st.subheader("Advanced System Behavior Metrics")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Publish Entropy",round(publish_entropy,3))
    c2.metric("KL Divergence",round(kl_divergence,3))
    c3.metric("Channel Gini Index",round(gini,3))
    c4.metric("Publishing Consistency",consistency_score)

    st.markdown("""
**Interpretation**

• Higher **entropy** → diverse publishing formats  
• Higher **KL divergence** → creation misaligned with publishing  
• Higher **Gini index** → publishing concentrated in few channels  
• Higher **consistency score** → stable publishing pipeline
""")

# -----------------------------------------------------
# FOOTER
# -----------------------------------------------------

st.divider()

st.caption(
    "Frammer AI Championship | Advanced Analytics + Optimization KPIs"
)
