import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# ---- PAGE SETUP & COLOUR THEME ----
st.set_page_config(page_title='Cost of Living', layout='wide')

st.markdown(
    "<h1 style='color:#2E5A88;'>Cost of Living: What the Headline Hides</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='color:#555; font-size:17px;'>"
    "The fastest-rising prices are not always the ones that hurt households most."
    "</p>",
    unsafe_allow_html=True
)

# ---- LOAD DATA ----
data = pd.read_csv('cost_of_living_merged.csv')


# ---- PLAIN-ENGLISH EXPLAINER (for non-technical readers) ----
with st.expander("ℹ️ How to read this: what 'rate', 'weight' and 'impact' mean"):
    st.markdown(
        """
        Every spending category has **two** numbers behind it:

        - **Rate** — how *fast* that category's prices are rising (e.g. transport up 6.8% in a year).
        - **Weight** — how *big a share* of a typical household's budget the category takes
          (e.g. housing is about a third of all spending).

        On their own, neither tells the full story. A price can rise fast but barely matter
        if you spend little on it — or rise slowly yet hurt a lot if it's a big part of your budget.

        So we combine them:

        > **Impact (weighted contribution) = rate × weight**

        This is the number that shows how much each category *actually adds to the cost of living*
        for a typical household. It is measured in **percentage points** — and all the categories'
        impacts added together equal the headline inflation figure you see in the news.

        *In short: the fastest-rising price is not always the one that hurts most — impact depends
        on how much you actually buy.*
        """
    )
    
# ============================================================
# SECTION 1: THE WHOLE PICTURE — pie, with its OWN month selector
# ============================================================
st.markdown("## Where inflation comes from")

month_pie = st.selectbox('Month for this chart', ['2026-Mar', '2026-Apr', '2026-May'], key='pie_month')
pie_month_data = data[data['month'] == month_pie]

st.caption("Each category's share of total inflation impact for the selected month. "
           "A pie gives the overall picture; similar small slices are hard to compare, "
           "so the ranked bars below zoom in on what matters.")

impact = pie_month_data[pie_month_data['weighted_contribution'] > 0].sort_values('weighted_contribution', ascending=False)
figP, axP = plt.subplots(figsize=(7, 7))
axP.pie(impact['weighted_contribution'], labels=impact['division_name'], autopct='%1.0f%%',
        textprops={'fontsize': 8})
axP.set_title(f'Share of total inflation impact ({month_pie})')
st.pyplot(figP)

# ============================================================
# SECTION 2: THE REVERSAL — two bars, with its OWN month selector
# ============================================================
st.markdown("## The reversal: fastest-rising vs most impactful")

month_bars = st.selectbox('Month for this comparison', ['2026-Mar', '2026-Apr', '2026-May'], key='bars_month')
bars_month_data = data[data['month'] == month_bars]

st.caption("Ranking the top six categories two ways reveals the insight: "
           "the fastest-rising prices are not the ones that hurt households most.")

col1, col2 = st.columns(2)

with col1:
    st.subheader('Fastest rising (top 6, by rate)')
    by_rate = bars_month_data.sort_values('annual_rate').tail(6)
    fig1, ax1 = plt.subplots()
    ax1.barh(by_rate['division_name'], by_rate['annual_rate'], color='#4C72B0')
    ax1.set_xlabel('Annual rate (%)')
    st.pyplot(fig1)

with col2:
    st.subheader('Hurts households most (top 6, by impact)')
    by_impact = bars_month_data.sort_values('weighted_contribution').tail(6)
    fig2, ax2 = plt.subplots()
    ax2.barh(by_impact['division_name'], by_impact['weighted_contribution'], color='#C44E52')
    ax2.set_xlabel('Weighted contribution (percentage points)')
    st.pyplot(fig2)

# ============================================================
# SECTION 3: TREND — line chart across ALL months (no month selector needed)
# ============================================================
st.markdown("## Trend across months")
st.caption("Hover over any point to see its value. Choose which categories to compare.")

categories = st.multiselect(
    'Choose categories to compare',
    options=sorted(data['division_name'].unique()),
    default=['Housing, water, electricity, gas and other fuels', 'Transport']
)

month_order = ['2026-Mar', '2026-Apr', '2026-May']
trend_data = data[data['division_name'].isin(categories)].copy()
trend_data['month'] = pd.Categorical(trend_data['month'], categories=month_order, ordered=True)
trend_data = trend_data.sort_values('month')

fig4 = px.line(
    trend_data, x='month', y='weighted_contribution', color='division_name', markers=True,
    labels={'weighted_contribution': 'Weighted contribution (pp)', 'month': 'Month',
            'division_name': 'Category'},
    title='How each category\'s impact changed, March to May 2026'
)
st.plotly_chart(fig4, use_container_width=True)