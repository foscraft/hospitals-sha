import plotly.express as px
import streamlit as st
from streamlit_card import card

def show_statistics(df):
    st.markdown("## 📊 Key Statistics")
    
    metrics = []
    if 'County' in df.columns:
        metrics.append(("No. Of Counties", df['County'].nunique(), "🌍"))
    if 'Sub_County' in df.columns:
        metrics.append(("No. Of Sub-Counties", df['Sub_County'].nunique(), "🗺️"))
    if 'Type' in df.columns:
        metrics.append(("Facility Types", df['Type'].nunique(), "🏥"))

    metrics.insert(0, ("Total No. Of Facilities", len(df), "🏥"))
    
    cols = st.columns(min(len(metrics), 4))
    for idx, (title, value, icon) in enumerate(metrics):
        with cols[idx % len(cols)]:
            card(
                title=f"{icon} {title}",
                text=f"{value:,}",
                styles={
                    "card": {
                        "width": "100%",
                        "height": "120px",
                        "border-radius": "12px",
                        "box-shadow": "0 6px 12px rgba(0,0,0,0.15)",
                        "text-align": "center",
                        "background-color": "#ffffff",
                    },
                    "title": {
                        "font-size": "1.1em",
                        "color": "#2c3e50",
                        "margin-bottom": "0.5em"
                    },
                    "text": {
                        "font-size": "2em",
                        "margin": "0",
                        "color": "#06304d"
                    }
                },
                key=f"stat_card_{idx}"
            )

def plot_charts(df):
    color_scheme = px.colors.qualitative.Plotly
    tab1, tab2 = st.tabs(["📈 Overview Charts", "🗺️ Geographic Distribution"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        if 'County' in df.columns:
            with col1:
                st.markdown("### Facilities by County")
                county_counts = df['County'].value_counts().reset_index()
                county_counts.columns = ['County', 'Count']
                fig_county = px.bar(
                    county_counts, 
                    x='County', 
                    y='Count', 
                    title="Facilities per County",
                    color='Count',
                    color_continuous_scale='Blues',
                    text='Count'
                )
                fig_county.update_traces(textposition='outside')
                fig_county.update_layout(
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(size=12),
                    margin=dict(t=50, b=150),
                    xaxis_tickangle=45
                )
                st.plotly_chart(fig_county, use_container_width=True)

        if 'Type' in df.columns:
            with col2:
                st.markdown("### Facility Types Distribution")
                type_counts = df['Type'].value_counts().reset_index()
                type_counts.columns = ['Type', 'Count']
                fig_type = px.pie(
                    type_counts, 
                    names='Type', 
                    values='Count', 
                    title="Distribution of Facility Types",
                    color_discrete_sequence=color_scheme
                )
                fig_type.update_traces(textposition='inside', textinfo='percent+label')
                fig_type.update_layout(
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5),
                    margin=dict(t=50)
                )
                st.plotly_chart(fig_type, use_container_width=True)

    with tab2:
        if 'Owner' in df.columns:
            st.markdown("### Facilities by Owner")
            owner_counts = df['Owner'].value_counts().reset_index()
            owner_counts.columns = ['Owner', 'Count']
            fig_owner = px.bar(
                owner_counts, 
                x='Owner', 
                y='Count', 
                title="Facilities by Owner",
                color='Owner',
                color_discrete_sequence=color_scheme,
                text='Count'
            )
            fig_owner.update_traces(textposition='outside')
            fig_owner.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12),
                margin=dict(t=50, b=150),
                xaxis_tickangle=45
            )
            st.plotly_chart(fig_owner, use_container_width=True)

        if 'Sub_County' in df.columns and 'County' in df.columns and 'Type' in df.columns:
            st.markdown("### Facility Hierarchy")
            df_hierarchy = df.groupby(['County', 'Sub_County', 'Type']).size().reset_index(name='Count')
            fig_treemap = px.treemap(
                df_hierarchy,
                path=['County', 'Sub_County', 'Type'],
                values='Count',
                title="Facility Distribution by County and Sub-County",
                color='Count',
                color_continuous_scale='Blues'
            )
            fig_treemap.update_layout(margin=dict(t=50))
            st.plotly_chart(fig_treemap, use_container_width=True)
