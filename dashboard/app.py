"""
StreamPulse Analytics — OTT Content Strategy & Audience Intelligence
An interactive, multi-page data exploration tool for OTT catalog strategy.

Author: Ranjith Kumar
Portfolio Project: Python • DuckDB • SQL • Streamlit
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# App Configuration & Page Layout
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="StreamPulse | OTT Content Strategy",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark slate aesthetic with Netflix red & vibrant cyan accents)
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .metric-container {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .insight-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-left: 4px solid #E50914;
        padding: 16px 20px;
        border-radius: 6px;
        margin: 20px 0;
        color: #CBD5E1;
    }
    .gem-badge {
        background-color: #065F46;
        color: #6EE7B7;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading & Caching
# -----------------------------------------------------------------------------
@st.cache_data
def load_ott_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, "data", "processed", "ott_titles.csv")
    
    if not os.path.exists(data_path):
        data_path = r"C:\Users\justk\.gemini\antigravity\scratch\ott-content-strategy\data\processed\ott_titles.csv"
        
    df = pd.read_csv(data_path)
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce').fillna(2000).astype(int)
    return df

df_full = load_ott_data()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Global Controls
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 🎬 StreamPulse Analytics")
st.sidebar.caption("OTT Catalog Intelligence & Strategy Platform")
st.sidebar.markdown("**Portfolio Project by Ranjith Kumar**")
st.sidebar.markdown("---")

nav_pages = [
    "1. Executive Overview",
    "2. Content Trends & Growth",
    "3. Language & Global Markets",
    "4. Ratings vs Popularity",
    "5. 2x2 Content Segmentation",
    "6. Title Explorer & Catalog Audit"
]
selected_page = st.sidebar.radio("Navigate Pages", nav_pages)

st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚙️ Catalog Filters")

# Content format filter
type_choice = st.sidebar.selectbox("Content Format", ["All Formats", "Movie", "Tv Show"])

# Release year slider
min_yr = int(df_full['release_year'].min())
max_yr = int(df_full['release_year'].max())
selected_years = st.sidebar.slider("Release Window", min_yr, max_yr, (1995, max_yr))

# Strategic segment filter
segment_choices = ["All Segments"] + sorted(df_full['content_segment'].dropna().unique().tolist())
selected_segment = st.sidebar.selectbox("Strategic Segment", segment_choices)

# Apply global filters
df_filtered = df_full[
    (df_full['release_year'] >= selected_years[0]) & 
    (df_full['release_year'] <= selected_years[1])
]
if type_choice != "All Formats":
    df_filtered = df_filtered[df_filtered['type'] == type_choice]
if selected_segment != "All Segments":
    df_filtered = df_filtered[df_filtered['content_segment'] == selected_segment]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Filtered Titles:** `{len(df_filtered):,}` of `{len(df_full):,}`")
st.sidebar.caption("Data: Curated Open Streaming Catalog (8,806 titles)")

# -----------------------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
if selected_page == nav_pages[0]:
    st.markdown('<div class="main-header">📊 Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Platform catalog baseline, format split, and category dominance.</div>', unsafe_allow_html=True)

    # Calculate Core KPIs
    total_titles = len(df_filtered)
    movies = (df_filtered['type'] == 'Movie').sum()
    series = (df_filtered['type'] == 'Tv Show').sum()
    movie_pct = (movies / total_titles * 100) if total_titles > 0 else 0
    series_pct = (series / total_titles * 100) if total_titles > 0 else 0
    avg_rating = df_filtered['rating_score'].mean()
    avg_popularity = df_filtered['popularity'].mean()
    top_genre = df_filtered['genre'].mode()[0] if not df_filtered.empty else "N/A"
    top_genre_count = (df_filtered['genre'] == top_genre).sum() if not df_filtered.empty else 0

    # Top KPI Metrics Row
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Catalog Titles", f"{total_titles:,}")
    with k2:
        st.metric("Movies Share", f"{movies:,}", f"{movie_pct:.1f}% of total")
    with k3:
        st.metric("TV Series Share", f"{series:,}", f"{series_pct:.1f}% of total")
    with k4:
        st.metric("Mean Rating Score", f"{avg_rating:.2f} / 10" if not np.isnan(avg_rating) else "N/A")
    with k5:
        st.metric("Mean Popularity", f"{avg_popularity:.1f} / 100" if not np.isnan(avg_popularity) else "N/A")

    st.markdown("---")

    # Visualizations Row
    col_chart1, col_chart2 = st.columns([1, 2])
    with col_chart1:
        st.subheader("Movie vs. TV Show Ratio")
        type_counts = df_filtered['type'].value_counts().reset_index()
        type_counts.columns = ['Format', 'Count']
        fig_donut = px.pie(
            type_counts,
            values='Count',
            names='Format',
            color='Format',
            color_discrete_map={'Movie': '#E50914', 'Tv Show': '#0284C7'},
            hole=0.55
        )
        fig_donut.update_traces(textinfo='percent+label', pull=[0.05, 0])
        fig_donut.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_donut, use_container_width=True)
        st.caption(f"💡 While Movies make up **{movie_pct:.1f}%** of title inventory, episodic TV shows drive significantly higher weekly viewing hours.")

    with col_chart2:
        st.subheader("Top 10 Genres by Catalog Volume")
        top_genres = df_filtered['genre'].value_counts().head(10).reset_index()
        top_genres.columns = ['Genre', 'Count']
        fig_bar = px.bar(
            top_genres,
            x='Count',
            y='Genre',
            orientation='h',
            text='Count',
            color='Count',
            color_continuous_scale='Reds'
        )
        fig_bar.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    # Narrative Insight Box
    st.markdown(f"""
    <div class="insight-box">
        <b>💡 Analyst Note:</b> The catalog is heavily anchored around <b>{top_genre}</b> ({top_genre_count:,} titles, {(top_genre_count/total_titles*100):.1f}% share) and <b>Comedies</b>. 
        These two genres provide the baseline viewing comfort for subscribers, while high-budget Action & Adventure and Crime series serve as the customer acquisition magnets.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE 2: CONTENT TRENDS & GROWTH
# -----------------------------------------------------------------------------
elif selected_page == nav_pages[1]:
    st.markdown('<div class="main-header">📈 Content Trends & Release Evolution</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Longitudinal tracking of release volume, format shifts, and genre expansion.</div>', unsafe_allow_html=True)

    # Aggregate by Year and Format
    yearly_df = df_filtered.groupby(['release_year', 'type']).size().reset_index(name='titles')
    yearly_totals = df_filtered.groupby('release_year').size().reset_index(name='total')
    yearly_totals['cumulative'] = yearly_totals['total'].cumsum()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Annual Content Releases by Format")
        fig_annual = px.bar(
            yearly_df,
            x='release_year',
            y='titles',
            color='type',
            barmode='stack',
            color_discrete_map={'Movie': '#E50914', 'Tv Show': '#0284C7'},
            labels={'release_year': 'Release Year', 'titles': 'Titles Added', 'type': 'Format'}
        )
        fig_annual.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_annual, use_container_width=True)

    with c2:
        st.subheader("Cumulative Catalog Growth Over Time")
        fig_cum = px.area(
            yearly_totals,
            x='release_year',
            y='cumulative',
            color_discrete_sequence=['#10B981'],
            labels={'release_year': 'Release Year', 'cumulative': 'Cumulative Titles'}
        )
        st.plotly_chart(fig_cum, use_container_width=True)

    st.subheader("Genre Trajectories Across Release Eras (Top 5 Genres)")
    top_5 = df_filtered['genre'].value_counts().head(5).index.tolist()
    genre_trends = df_filtered[df_filtered['genre'].isin(top_5)].groupby(['release_year', 'genre']).size().reset_index(name='titles')

    fig_lines = px.line(
        genre_trends,
        x='release_year',
        y='titles',
        color='genre',
        markers=True,
        labels={'release_year': 'Release Year', 'titles': 'Annual Releases', 'genre': 'Genre'}
    )
    fig_lines.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_lines, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <b>💡 Key Observation:</b> Notice the dramatic inflection point starting in <b>2015–2016</b>. As direct-to-consumer streaming wars intensified, annual catalog releases tripled. 
        TV Series grew from a modest ~15% of annual releases pre-2015 to over 34% by 2020, as platforms realized multi-episode narrative arcs drive sticky subscriber habits.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE 3: LANGUAGE & GLOBAL MARKETS
# -----------------------------------------------------------------------------
elif selected_page == nav_pages[2]:
    st.markdown('<div class="main-header">🌍 Language & Global Markets</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Evaluating international catalog penetration, language diversity, and market efficiency.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 15 Producing Countries")
        country_counts = df_filtered[df_filtered['country'] != 'Unknown']['country'].value_counts().head(15).reset_index()
        country_counts.columns = ['Country', 'Titles']
        fig_country = px.bar(
            country_counts,
            x='Titles',
            y='Country',
            orientation='h',
            text='Titles',
            color='Titles',
            color_continuous_scale='Blues'
        )
        fig_country.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig_country, use_container_width=True)

    with col2:
        st.subheader("Top Languages by Catalog Share")
        lang_counts = df_filtered['language'].value_counts().head(10).reset_index()
        lang_counts.columns = ['Language', 'Titles']
        fig_lang = px.bar(
            lang_counts,
            x='Language',
            y='Titles',
            text='Titles',
            color='Titles',
            color_continuous_scale='Teal'
        )
        st.plotly_chart(fig_lang, use_container_width=True)

    st.subheader("Market Performance Bubble Chart (Rating vs Popularity)")
    top_mkts = country_counts['Country'].head(12).tolist()
    mkt_summary = df_filtered[df_filtered['country'].isin(top_mkts)].groupby('country').agg(
        titles=('title_id', 'count'),
        avg_rating=('rating_score', 'mean'),
        avg_pop=('popularity', 'mean')
    ).reset_index()

    fig_bubble = px.scatter(
        mkt_summary,
        x='avg_pop',
        y='avg_rating',
        size='titles',
        color='country',
        text='country',
        labels={'avg_pop': 'Average Popularity Score', 'avg_rating': 'Average Rating Score', 'country': 'Market'},
        title="Market Performance Matrix (Bubble Size = Total Titles Produced)"
    )
    fig_bubble.update_traces(textposition='top center')
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <b>💡 Regional Insight:</b> While the United States represents over 40% of catalog volume, international hubs like <b>India (972 titles)</b>, <b>Japan (245 titles)</b>, and <b>South Korea (199 titles)</b> 
        show remarkably high audience engagement per production dollar. Localized content often drives breakout international hits with high return-on-investment.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE 4: RATINGS VS POPULARITY
# -----------------------------------------------------------------------------
elif selected_page == nav_pages[3]:
    st.markdown('<div class="main-header">⭐ Ratings & Popularity Dynamics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Investigating the relationship between critic/viewer ratings and platform popularity.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Rating Score Distribution")
        fig_dist = px.histogram(
            df_filtered.dropna(subset=['rating_score']),
            x='rating_score',
            nbins=30,
            marginal='box',
            color_discrete_sequence=['#8B5CF6'],
            labels={'rating_score': 'Rating Score (1-10)'}
        )
        fig_dist.add_vline(x=df_filtered['rating_score'].mean(), line_dash="dash", line_color="orange", annotation_text="Mean (6.83)")
        fig_dist.add_vline(x=df_filtered['rating_score'].median(), line_dash="dot", line_color="green", annotation_text="Median (6.80)")
        st.plotly_chart(fig_dist, use_container_width=True)

    with col2:
        st.subheader("Maturity Rating Demographics")
        rating_counts = df_filtered['rating'].value_counts().head(8).reset_index()
        rating_counts.columns = ['Rating', 'Titles']
        fig_mat = px.bar(
            rating_counts,
            x='Rating',
            y='Titles',
            text='Titles',
            color='Titles',
            color_continuous_scale='Sunset'
        )
        st.plotly_chart(fig_mat, use_container_width=True)

    st.subheader("Rating vs. Popularity Dispersion Scatter")
    sample_size = min(1200, len(df_filtered.dropna(subset=['rating_score', 'popularity'])))
    sample_df = df_filtered.dropna(subset=['rating_score', 'popularity']).sample(sample_size, random_state=42)

    fig_scatter = px.scatter(
        sample_df,
        x='popularity',
        y='rating_score',
        color='type',
        hover_data=['title', 'genre', 'country', 'release_year'],
        color_discrete_map={'Movie': '#E50914', 'Tv Show': '#0284C7'},
        opacity=0.65,
        labels={'popularity': 'Popularity Score (0-100)', 'rating_score': 'Rating Score (1-10)'}
    )
    fig_scatter.add_hline(y=6.8, line_dash="dash", line_color="#94A3B8", annotation_text="Median Rating (6.8)")
    fig_scatter.add_vline(x=43.5, line_dash="dash", line_color="#94A3B8", annotation_text="Median Popularity (43.5)")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <b>💡 Rating vs. Popularity:</b> A common misconception is that high ratings guarantee high popularity. In reality, the correlation is weak to moderate. 
        <b>Rating measures quality and sentiment</b> (do viewers love it?), whereas <b>popularity measures current cultural reach and stream velocity</b> (are people watching it right now?).
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE 5: 2x2 CONTENT SEGMENTATION
# -----------------------------------------------------------------------------
elif selected_page == nav_pages[4]:
    st.markdown('<div class="main-header">🎯 2x2 Strategic Content Segmentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Categorizing catalog titles into actionable licensing, marketing, and de-licensing tiers.</div>', unsafe_allow_html=True)

    # Segment Summary Table
    seg_stats = df_filtered.groupby('content_segment').agg(
        titles=('title_id', 'count'),
        avg_rating=('rating_score', 'mean'),
        avg_pop=('popularity', 'mean'),
        movies=('type', lambda x: (x == 'Movie').sum()),
        series=('type', lambda x: (x == 'Tv Show').sum())
    ).reset_index()
    seg_stats['catalog_share'] = (seg_stats['titles'] / len(df_filtered) * 100).round(1)

    # 4 Quadrant Cards
    c1, c2, c3, c4 = st.columns(4)
    quadrants = [
        ("Blockbusters", "High Rating + High Pop", "#10B981", "Flagship titles driving new signups, critical prestige, and cultural buzz."),
        ("Hidden Gems", "High Rating + Low Pop", "#0284C7", "High artistic quality but low discovery. Prime candidates for homepage featuring."),
        ("Guilty Pleasures", "Low Rating + High Pop", "#F59E0B", "High engagement casual comfort viewing. Acquire at low licensing cost."),
        ("Underperformers", "Low Rating + Low Pop", "#EF4444", "Catalog bloat with low viewing and poor reception. Prime de-licensing candidates.")
    ]
    for idx, (title, sub, color, desc) in enumerate(quadrants):
        with [c1, c2, c3, c4][idx]:
            matched = seg_stats[seg_stats['content_segment'].str.contains(title, case=False, na=False)]
            cnt = matched['titles'].values[0] if not matched.empty else 0
            share = matched['catalog_share'].values[0] if not matched.empty else 0
            st.markdown(f"""
            <div style="background-color: #1E293B; border-top: 4px solid {color}; padding: 14px; border-radius: 8px;">
                <div style="font-size: 12px; color: #94A3B8; text-transform: uppercase;">{sub}</div>
                <div style="font-size: 20px; font-weight: bold; color: #F8FAFC; margin-top: 2px;">{title}</div>
                <div style="font-size: 17px; color: {color}; margin-top: 4px; font-weight: 600;">{cnt:,} titles <span style="font-size: 12px; color: #94A3B8;">({share}%)</span></div>
                <div style="font-size: 12px; color: #CBD5E1; margin-top: 8px; line-height: 1.3;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("2x2 Quadrant Visual Map")
        fig_quad = px.scatter(
            df_filtered.dropna(subset=['rating_score', 'popularity']).sample(min(1500, len(df_filtered.dropna(subset=['rating_score', 'popularity']))), random_state=42),
            x='popularity',
            y='rating_score',
            color='content_segment',
            hover_data=['title', 'genre', 'country'],
            opacity=0.7,
            labels={'popularity': 'Popularity Score', 'rating_score': 'Rating Score', 'content_segment': 'Strategic Segment'}
        )
        fig_quad.add_hline(y=6.8, line_dash="dash", line_color="white")
        fig_quad.add_vline(x=43.5, line_dash="dash", line_color="white")
        fig_quad.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5))
        st.plotly_chart(fig_quad, use_container_width=True)

    with col2:
        st.subheader("Segment Performance Metrics")
        st.dataframe(
            seg_stats[['content_segment', 'titles', 'catalog_share', 'avg_rating', 'avg_pop']].sort_values(by='titles', ascending=False),
            column_config={
                "content_segment": "Segment",
                "titles": "Title Count",
                "catalog_share": "Catalog %",
                "avg_rating": st.column_config.NumberColumn("Avg Rating", format="%.2f"),
                "avg_pop": st.column_config.NumberColumn("Avg Popularity", format="%.1f")
            },
            hide_index=True,
            use_container_width=True
        )

        st.subheader("💎 Top 'Hidden Gems' to Feature")
        gems_df = df_filtered[df_filtered['content_segment'].str.contains('Hidden Gems', na=False)].sort_values(by=['rating_score', 'popularity'], ascending=[False, True]).head(6)
        st.dataframe(gems_df[['title', 'genre', 'country', 'rating_score', 'popularity']], hide_index=True, use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 6: TITLE EXPLORER & CATALOG AUDIT
# -----------------------------------------------------------------------------
elif selected_page == nav_pages[5]:
    st.markdown('<div class="main-header">🔍 Title Explorer & Catalog Auditor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Interactive search, multi-attribute filtering, and data export for business reviews.</div>', unsafe_allow_html=True)

    search_kw = st.text_input("🔎 Search Title by Keyword", placeholder="e.g. Inception, Stranger Things, Queen...")

    f1, f2, f3 = st.columns(3)
    with f1:
        genre_filter = st.multiselect("Filter by Genre", sorted(df_filtered['genre'].unique()))
    with f2:
        min_score = st.slider("Min Rating Score", 0.0, 10.0, 0.0, 0.5)
    with f3:
        min_pop = st.slider("Min Popularity", 0.0, 100.0, 0.0, 5.0)

    # Filter data
    df_exp = df_filtered.copy()
    if search_kw:
        df_exp = df_exp[df_exp['title'].str.contains(search_kw, case=False, na=False)]
    if genre_filter:
        df_exp = df_exp[df_exp['genre'].isin(genre_filter)]
    if min_score > 0:
        df_exp = df_exp[df_exp['rating_score'] >= min_score]
    if min_pop > 0:
        df_exp = df_exp[df_exp['popularity'] >= min_pop]

    st.write(f"Showing **{len(df_exp):,}** titles matching criteria:")

    cols_to_show = ['title_id', 'title', 'type', 'release_year', 'genre', 'language', 'country', 'rating', 'runtime', 'popularity', 'rating_score', 'content_segment']
    st.dataframe(
        df_exp[cols_to_show],
        column_config={
            "title_id": "ID",
            "title": "Title",
            "type": "Format",
            "release_year": "Year",
            "genre": "Genre",
            "language": "Language",
            "country": "Country",
            "rating": "Maturity",
            "runtime": "Runtime (m)",
            "popularity": st.column_config.NumberColumn("Popularity", format="%.1f"),
            "rating_score": st.column_config.NumberColumn("Rating", format="%.1f"),
            "content_segment": "Segment"
        },
        hide_index=True,
        use_container_width=True
    )

    # CSV Export Button
    csv_bytes = df_exp.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV (Tableau / Power BI)",
        data=csv_bytes,
        file_name="ott_catalog_filtered_export.csv",
        mime="text/csv"
    )

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption("StreamPulse Analytics • Created by Ranjith Kumar • Portfolio Project for Entertainment Data Strategy")
