import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path


# Load Data
file_path = r"C:\Users\janki\OneDrive\Desktop\vgsales_dashboard_app\vgsales_dashboard.xlsm"
df = pd.read_excel(file_path, engine="openpyxl")


# Preprocessing
df.dropna(subset=['Genre', 'Publisher', 'Platform', 'Year', 'Name'], inplace=True)
df['Total_Sales'] = df['Total_Sales'].astype(float) * 1e6  # Convert to actual copies
sales_col = 'Total_Sales'

# Sidebar Filters
st.sidebar.header("🔍 Filters")
# Region Mapping (fix for KeyError)
region_mapping = {
    'Global_Sales': 'Total_Sales',
    'NA_Sales': 'NA_Sales',
    'EU_Sales': 'EU_Sales',
    'JP_Sales': 'JP_Sales',
    'Other_Sales': 'Other_Sales'
}

# Filter dropdown (note: Global_Sales maps to Total_Sales)
region_label = st.sidebar.selectbox("Select Region", list(region_mapping.keys()))
region = region_mapping[region_label]

years = st.sidebar.slider("Publishing Year Range", int(df['Year'].min()), int(df['Year'].max()), (2000, 2010))
platforms = st.sidebar.multiselect("Select Platforms", df['Platform'].unique())
publishers = st.sidebar.multiselect("Select Publishers", df['Publisher'].unique())

# Apply Filters
filtered_df = df[(df['Year'] >= years[0]) & (df['Year'] <= years[1])]
if platforms:
    filtered_df = filtered_df[filtered_df['Platform'].isin(platforms)]
if publishers:
    filtered_df = filtered_df[filtered_df['Publisher'].isin(publishers)]

# Header
st.title("🎮 Video Games Sales Dashboard")

# KPIs
st.metric("Total Game Copies Sold", f"{filtered_df[region].sum()/1e9:.2f} Bn")
st.metric("Games Published", f"{len(filtered_df):,}")

# Treemap - Top Platforms
platform_data = filtered_df.groupby('Platform')[region].sum().nlargest(10).reset_index()
fig1 = px.treemap(platform_data, path=['Platform'], values=region, title="Top 10 Platforms")
st.plotly_chart(fig1, use_container_width=True)

# Genre Sales Bar Chart
genre_data = filtered_df.groupby('Genre')[region].sum().reset_index()
fig2 = px.bar(genre_data, x='Genre', y=region, title="Games Sold by Genre", color='Genre')
st.plotly_chart(fig2, use_container_width=True)

# Donut Chart - Top Games
top_games = filtered_df.groupby('Name')[region].sum().nlargest(10).reset_index()
fig3 = go.Figure(go.Pie(labels=top_games['Name'], values=top_games[region], hole=0.4))
fig3.update_layout(title="Top 10 Games by Copies Sold")
st.plotly_chart(fig3, use_container_width=True)

# Bubble Chart - Top Publishers
pub_stats = filtered_df.groupby('Publisher').agg({
    region: 'sum',
    'Name': 'count'
}).rename(columns={'Name': 'Games_Published'}).nlargest(10, region).reset_index()

fig4 = px.scatter(pub_stats, x='Games_Published', y=region,
                  size=region, color='Publisher',
                  title='Top Publishers by Sales & Games Published',
                  size_max=60)
st.plotly_chart(fig4, use_container_width=True)

# Bar Chart - Games Published by Year
yearly_data = filtered_df.groupby('Year')['Name'].count().reset_index()
fig5 = px.bar(yearly_data, x='Year', y='Name', title="Games Published by Year", color='Name')
st.plotly_chart(fig5, use_container_width=True)



# (Your existing code above remains the same)

# =============================================
# NEW VISUALIZATIONS TO ADD AT THE END
# =============================================

# 1. Sales vs. Year Scatter Plot (with size as sales)
st.header("📈 Sales Distribution Over Years")
fig6 = px.scatter(
    filtered_df,
    x='Year',
    y=region,
    size=region,
    color='Platform',
    hover_name='Name',
    title=f'Sales Distribution by Year ({region_label})',
    labels={region: 'Sales (in millions)'},
    size_max=30,
    opacity=0.7
)
fig6.update_traces(marker=dict(line=dict(width=0.5, color='DarkSlateGrey')))
st.plotly_chart(fig6, use_container_width=True)

# 2. Platform vs Publisher Heatmap
st.header("🔥 Platform-Publisher Sales Heatmap")
platform_pub = filtered_df.groupby(['Platform', 'Publisher'])[region].sum().unstack().fillna(0)
fig7 = px.imshow(
    platform_pub,
    labels=dict(x="Publisher", y="Platform", color="Sales"),
    title=f"Sales Heatmap: Platform vs Publisher ({region_label})",
    color_continuous_scale='Viridis'
)
st.plotly_chart(fig7, use_container_width=True)

# 3. Genre Popularity Over Time (Animated Scatter)
st.header("🕰️ Genre Popularity Evolution")
genre_year = filtered_df.groupby(['Year', 'Genre'])[region].sum().reset_index()
fig8 = px.scatter(
    genre_year,
    x='Year',
    y=region,
    color='Genre',
    size=region,
    animation_frame='Year',
    range_x=[years[0]-1, years[1]+1],
    title=f"Genre Popularity Over Time ({region_label})",
    hover_name='Genre',
    size_max=45
)
fig8.update_layout(transition={'duration': 1000})
st.plotly_chart(fig8, use_container_width=True)

# 4. Publisher Performance Comparison
st.header("🏆 Publisher Performance Comparison")
top_publishers = filtered_df.groupby('Publisher')[region].sum().nlargest(5).index.tolist()
publisher_comparison = filtered_df[filtered_df['Publisher'].isin(top_publishers)]
fig9 = px.strip(
    publisher_comparison,
    x='Publisher',
    y=region,
    color='Publisher',
    hover_name='Name',
    title=f"Game Sales Distribution by Top Publishers ({region_label})",
    log_y=True
)
fig9.update_traces(jitter=0.4)
st.plotly_chart(fig9, use_container_width=True)