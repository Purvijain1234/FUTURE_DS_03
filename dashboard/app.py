import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Marketing Funnel Dashboard",
    layout="wide",
    page_icon="📊"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background: linear-gradient(to right, #0f172a, #111827);
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

h1, h2, h3 {
    color: white;
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "2019-Nov.csv",
        nrows=1000000
    )

    df['event_time'] = pd.to_datetime(df['event_time'])

    df['brand'] = df['brand'].fillna("Unknown")
    df['category_code'] = df['category_code'].fillna("Unknown")

    df['hour'] = df['event_time'].dt.hour
    df['day'] = df['event_time'].dt.day_name()
    df['date'] = df['event_time'].dt.date

    return df

df = load_data()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("📌 Dashboard Filters")

event_filter = st.sidebar.multiselect(
    "Select Event Type",
    df['event_type'].unique(),
    default=df['event_type'].unique()
)

brand_filter = st.sidebar.multiselect(
    "Select Brand",
    df['brand'].value_counts().head(20).index,
    default=df['brand'].value_counts().head(10).index
)

df = df[
    (df['event_type'].isin(event_filter)) &
    (df['brand'].isin(brand_filter))
]

# =========================================================
# TITLE
# =========================================================

st.title("📊 Marketing Funnel & Conversion Dashboard")

st.markdown("""
Analyze customer behavior, product engagement,
conversion trends, and funnel performance
in a multi-category e-commerce platform.
""")

st.markdown("---")

# =========================================================
# KPI CALCULATIONS
# =========================================================

total_users = df['user_id'].nunique()
total_events = len(df)

views = len(df[df['event_type'] == 'view'])
cart = len(df[df['event_type'] == 'cart'])
purchase = len(df[df['event_type'] == 'purchase'])

view_to_cart = round((cart/views)*100,2) if views != 0 else 0
cart_to_purchase = round((purchase/cart)*100,2) if cart != 0 else 0

avg_price = round(df['price'].mean(),2)

# =========================================================
# KPI SECTION
# =========================================================

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("👤 Users", f"{total_users:,}")

with col2:
    st.metric("📦 Events", f"{total_events:,}")

with col3:
    st.metric("👀 Views", f"{views:,}")

with col4:
    st.metric("🛒 Cart", f"{cart:,}")

with col5:
    st.metric("💳 Purchases", f"{purchase:,}")

with col6:
    st.metric("💰 Avg Price", f"${avg_price}")

st.markdown("---")

# =========================================================
# FUNNEL + PIE
# =========================================================

col1, col2 = st.columns(2)

# -------------------------
# FUNNEL CHART
# -------------------------

with col1:

    st.subheader("📈 Funnel Analysis")

    funnel_df = pd.DataFrame({
        "Stage": ["Views", "Cart", "Purchase"],
        "Count": [views, cart, purchase]
    })

    fig = px.funnel(
        funnel_df,
        x='Count',
        y='Stage',
        color='Stage',
        color_discrete_sequence=[
            '#8B5CF6',
            '#06B6D4',
            '#10B981'
        ]
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# EVENT DISTRIBUTION
# -------------------------

with col2:

    st.subheader("📊 Event Distribution")

    fig = px.pie(
        df,
        names='event_type',
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================================================
# PRICE + PURCHASE TREND
# =========================================================

col1, col2 = st.columns(2)

# -------------------------
# PRICE DISTRIBUTION
# -------------------------

with col1:

    st.subheader("💰 Price Distribution")

    fig = px.histogram(
        df,
        x='price',
        nbins=50,
        color_discrete_sequence=['#06B6D4']
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# PURCHASES BY HOUR
# -------------------------

with col2:

    st.subheader("⏰ Purchases by Hour")

    purchase_df = df[df['event_type'] == 'purchase']

    hourly = (
        purchase_df.groupby('hour')
        .size()
        .reset_index(name='count')
    )

    fig = px.line(
        hourly,
        x='hour',
        y='count',
        markers=True,
        color_discrete_sequence=['#F59E0B']
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================================================
# TOP CATEGORIES + TOP BRANDS
# =========================================================

col1, col2 = st.columns(2)

# -------------------------
# TOP CATEGORIES
# -------------------------

with col1:

    st.subheader("🏆 Top Categories")

    top_categories = (
        df['category_code']
        .value_counts()
        .head(10)
    )

    fig = px.bar(
        x=top_categories.values,
        y=top_categories.index,
        orientation='h',
        color=top_categories.values,
        color_continuous_scale='Purples'
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# TOP BRANDS
# -------------------------

with col2:

    st.subheader("🔥 Top Brands")

    top_brands = (
        df['brand']
        .value_counts()
        .head(10)
    )

    fig = px.treemap(
        names=top_brands.index,
        parents=[""] * len(top_brands),
        values=top_brands.values,
        color=top_brands.values,
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================================================
# CATEGORY ANALYSIS + USER ACTIVITY
# =========================================================

col1, col2 = st.columns(2)

# -------------------------
# CATEGORY VS EVENT TYPE
# -------------------------

with col1:

    st.subheader("📦 Category vs Event Type")

    category_event = (
        df.groupby(['category_code', 'event_type'])
        .size()
        .reset_index(name='count')
    )

    top_cat = (
        df['category_code']
        .value_counts()
        .head(10)
        .index
    )

    category_event = category_event[
        category_event['category_code'].isin(top_cat)
    ]

    fig = px.bar(
        category_event,
        x='category_code',
        y='count',
        color='event_type',
        barmode='stack',
        color_discrete_sequence=[
            '#8B5CF6',
            '#06B6D4',
            '#10B981',
            '#F59E0B'
        ]
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# TOP USER ACTIVITY
# -------------------------

with col2:

    st.subheader("👤 Top User Activity")

    top_users = (
        df['user_id']
        .value_counts()
        .head(20)
        .reset_index()
    )

    top_users.columns = ['user_id', 'activity']

    fig = px.scatter(
        top_users,
        x='user_id',
        y='activity',
        size='activity',
        color='activity',
        color_continuous_scale='Tealgrn'
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================================================
# DAILY USERS + AVG PRICE
# =========================================================

col1, col2 = st.columns(2)

# -------------------------
# DAILY ACTIVE USERS
# -------------------------

with col1:

    st.subheader("📅 Daily Active Users")

    daily_users = (
        df.groupby('date')['user_id']
        .nunique()
        .reset_index()
    )

    fig = px.area(
        daily_users,
        x='date',
        y='user_id',
        color_discrete_sequence=['#8B5CF6']
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# AVG PRICE BY EVENT TYPE
# -------------------------

with col2:

    st.subheader("💰 Avg Price by Event Type")

    avg_price_event = (
        df.groupby('event_type')['price']
        .mean()
        .reset_index()
    )

    fig = px.bar(
        avg_price_event,
        x='event_type',
        y='price',
        color='event_type',
        color_discrete_sequence=[
            '#8B5CF6',
            '#06B6D4',
            '#10B981',
            '#F59E0B'
        ]
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================================================
# INSIGHTS
# =========================================================

st.subheader("📌 Key Business Insights")

st.markdown("""
- Product views are significantly higher than purchases.

- Major customer drop-off occurs between View and Cart stages.

- Mid-priced products achieve better engagement.

- Certain categories dominate customer interactions.

- Purchase activity peaks during specific hours.

- Cart abandonment impacts overall conversion rates.
""")

# =========================================================
# RECOMMENDATIONS
# =========================================================

st.subheader("🚀 Recommendations")

st.markdown("""
- Improve product page quality
- Simplify checkout process
- Retarget abandoned cart users
- Promote top-performing categories
- Run campaigns during peak activity hours
- Use personalized recommendations
""")