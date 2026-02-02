import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go


# 1. Database Connection
def load_data():
    # Using a context manager for safer connection handling
    # Note: Ensure mins.db is in the same directory as this script
    with sqlite3.connect('mins.db') as conn:
        query = "SELECT * FROM mins"
        df = pd.read_sql_query(query, conn)
    
    df['time'] = pd.to_datetime(df['time'])
    return df

st.set_page_config(layout="wide")
st.title("📈 Advanced Stock Market Viewer")

try:
    df = load_data()

    # --- SIDEBAR CONTROLS ---
    st.sidebar.header("Chart Settings")
    
    # Symbol Selection
    symbols = df['symbol'].unique()
    selected_symbol = st.sidebar.selectbox("Select Symbol", symbols)
    
    # --- NEW: Date Selection Logic ---
    st.sidebar.markdown("---")
    view_mode = st.sidebar.radio("View Mode", ["Single Day", "All History"])
    
    # Get unique dates for the selected symbol
    available_dates = sorted(df[df['symbol'] == selected_symbol]['time'].dt.date.unique(), reverse=True)
    
    if view_mode == "Single Day":
        selected_date = st.sidebar.selectbox("Select Trading Date", available_dates)
        # Filter for symbol AND specific date
        mask = (df['symbol'] == selected_symbol) & (df['time'].dt.date == selected_date)
    else:
        # Filter for symbol only
        mask = (df['symbol'] == selected_symbol)
    
    # Toggle for technical indicators
    st.sidebar.markdown("---")
    show_sma_fast = st.sidebar.checkbox("Show 20-period SMA", value=True)
    show_sma_slow = st.sidebar.checkbox("Show 50-period SMA", value=False)

    # --- DATA PROCESSING ---
    filtered_df = df[mask].sort_values('time').copy()
    
    # Calculate Moving Averages (Calculated on the filtered subset)
    if len(filtered_df) > 0:
        filtered_df['SMA_20'] = filtered_df['close'].rolling(window=20).mean()
        filtered_df['SMA_50'] = filtered_df['close'].rolling(window=50).mean()

        # --- CHART SECTION ---
        fig = go.Figure()

        # 1. Add Candlestick Trace
        fig.add_trace(go.Candlestick(
            x=filtered_df['time'],
            open=filtered_df['open'],
            high=filtered_df['high'],
            low=filtered_df['low'],
            close=filtered_df['close'],
            name="Price Action"
        ))

        # 2. Add Fast SMA Line
        if show_sma_fast:
            fig.add_trace(go.Scatter(
                x=filtered_df['time'],
                y=filtered_df['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='cyan', width=1.5)
            ))

        # 3. Add Slow SMA Line
        if show_sma_slow:
            fig.add_trace(go.Scatter(
                x=filtered_df['time'],
                y=filtered_df['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='orange', width=1.5)
            ))

        # Layout Styling
        title_suffix = f" - {selected_date}" if view_mode == "Single Day" else " - All History"
        fig.update_layout(
            title=f"{selected_symbol}{title_suffix}",
            xaxis_rangeslider_visible=False, 
            template="plotly_dark",
            height=600,
            yaxis_title="Price",
            xaxis_title="Time"
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- TABLE SECTION ---
        with st.expander("View Raw Data"):
            st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("No data found for the selected filters.")

except Exception as e:
    st.error(f"Error loading database: {e}")