#!/usr/bin/env python3
"""Football Manager Scout Application - Streamlit Version

This module provides a modern web UI for scouting players in Football Manager
using Streamlit for the interface and scout_app.py for analysis logic.
"""

import streamlit as st
import pandas as pd
import numpy as np
from scout_app import detect_columns, parse_value, normalize, calculate_tactical_dimensions, age_factor

# Import role-specific scoring functions
from coff import calculate_coff_score
from strika import calculate_striker_score
from goalkeeper import calculate_goalkeeper_score
from defensive_mid import calculate_defensive_score
from defenders import calculate_defender_score
from fullbacks import calculate_fullback_score
from winger import calculate_offensive_score

# Page configuration
st.set_page_config(
    page_title="FM Scout Gem",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #0d1117;
    }
    .stApp {
        background-color: #0d1117;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #58a6ff !important;
    }
    .stMarkdown, .stDataFrame, .stTable {
        color: #f5f5f5 !important;
    }
    .sidebar .stMarkdown, .sidebar .stNumberInput, .sidebar .stSlider {
        color: #f5f5f5 !important;
    }
    .stSidebar {
        background-color: #161b22;
    }
    .stButton>button {
        background-color: #238636;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2ea043;
    }
    .info-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        background-color: #1a2535;
        border: 1px solid #58a6ff;
        color: #58a6ff;
    }
    .success-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        background-color: #14261a;
        border: 1px solid #3fb950;
        color: #3fb950;
    }
    /* Force table text color */
    div[data-testid="stDataFrame"] table,
    div[data-testid="stTable"] table {
        color: #f5f5f5 !important;
    }
    div[data-testid="stDataFrame"] th,
    div[data-testid="stTable"] th {
        color: #58a6ff !important;
    }
</style>
""", unsafe_allow_html=True)

def process_analysis(df, min_price, price_threshold, min_apps, max_age, min_age,
                     include_coff, include_striker, include_winger, include_defenders,
                     include_defensive_mid, include_fullbacks, include_goalkeeper):
    """Process dataframe and analyze players based on filters.
    
    Args:
        df: Input DataFrame
        min_price: Minimum price in millions €
        price_threshold: Maximum price in millions €
        min_apps: Minimum appearances
        max_age: Maximum age
        min_age: Minimum age
        include_coff: Include attacking midfielders (coff)
        include_striker: Include strikers
        include_winger: Include wingers
        include_defenders: Include defenders
        include_defensive_mid: Include defensive midfielders
        include_fullbacks: Include fullbacks
        include_goalkeeper: Include goalkeepers
        
    Returns:
        tuple: (sorted_df, role_scores, info_text) or (None, None, error_message)
    """
    try:
        # Detect columns automatically
        cm = detect_columns(df)
        
        # Parse Guide Value to numeric _price in €
        df = df.copy()
        df['_price'] = pd.to_numeric(df[cm['Guide Value']].apply(lambda x: parse_value(x)), errors='coerce').fillna(0)
        df['_age'] = pd.to_numeric(df[cm['Age']], errors='coerce').fillna(0)
        df['_apps'] = pd.to_numeric(df[cm['Appearances']], errors='coerce').fillna(0)
        
        # Apply filters (prices in millions, convert to € for filtering)
        min_price_euros = min_price * 1_000_000
        max_price_euros = price_threshold * 1_000_000
        
        filtered_df = df[
            (df['_price'] >= min_price_euros) &
            (df['_price'] <= max_price_euros) &
            (df['_apps'] >= min_apps) &
            (df['_age'] >= min_age) &
            (df['_age'] < max_age)
        ].copy()
        
        if len(filtered_df) == 0:
            return None, None, f"⚠️ No players match the criteria. Try adjusting filters. (Filtered {len(df)} → 0 players)"
        
        # Calculate role-specific scores using correct coefficients
        role_scores = {}
        
        # COFF (Attacking Mid) - calculate_coff_score from coff.py
        if include_coff:
            filtered_df['_coff_score'] = filtered_df.apply(calculate_coff_score, axis=1)
            role_scores['coff'] = '_coff_score'
        
        # Striker - calculate_striker_score from strika.py
        if include_striker:
            filtered_df['_striker_score'] = filtered_df.apply(calculate_striker_score, axis=1)
            role_scores['strika'] = '_striker_score'
        
        # Goalkeeper - calculate_goalkeeper_score from goalkeeper.py
        if include_goalkeeper:
            filtered_df['_gk_score'] = filtered_df.apply(calculate_goalkeeper_score, axis=1)
            role_scores['goalkeeper'] = '_gk_score'
        
        # Defensive Mid - calculate_defensive_score from defensive_mid.py
        if include_defensive_mid:
            filtered_df['_dm_score'] = filtered_df.apply(calculate_defensive_score, axis=1)
            role_scores['defensive_mid'] = '_dm_score'
        
        # Defenders - calculate_defender_score from defenders.py
        if include_defenders:
            filtered_df['_def_score'] = filtered_df.apply(calculate_defender_score, axis=1)
            role_scores['defenders'] = '_def_score'
        
        # Fullbacks - calculate_fullback_score from fullbacks.py
        if include_fullbacks:
            filtered_df['_fb_score'] = filtered_df.apply(calculate_fullback_score, axis=1)
            role_scores['fullbacks'] = '_fb_score'
        
        # Winger - calculate_offensive_score from winger.py
        if include_winger:
            filtered_df['_winger_score'] = filtered_df.apply(calculate_offensive_score, axis=1)
            role_scores['winger'] = '_winger_score'
        
        if not role_scores:
            return None, None, "⚠️ No roles selected. Please enable at least one position filter."
        
        # Use the primary score column for sorting (combine all active roles)
        score_columns = list(role_scores.values())
        filtered_df['_total_score'] = filtered_df[score_columns].sum(axis=1)
        
        # Apply age factor
        filtered_df['Age Factor'] = filtered_df['_age'].apply(age_factor)
        
        # Calculate Value Index: (Score * Age Factor) / (_price in millions)
        valid_price = filtered_df['_price'].replace(0, float('inf'))
        value_index_raw = (filtered_df['_total_score'] * filtered_df['Age Factor']) / (valid_price / 1_000_000)
        raw_value_index = value_index_raw.replace([float('inf'), float('-inf')], float('nan')).fillna(0)
        
        # Normalize Value Index to 0-100 scale
        if len(raw_value_index) > 0:
            max_val = raw_value_index.max()
            if max_val > 0:
                normalized_vi = (raw_value_index / max_val * 100).round(2)
                filtered_df['Value Index'] = normalized_vi.clip(upper=100)
            else:
                filtered_df['Value Index'] = 0
        else:
            filtered_df['Value Index'] = 0
        
        # Sort by Value Index descending
        sorted_df = filtered_df.sort_values('Value Index', ascending=False).reset_index(drop=True)
        
        if len(sorted_df) == 0:
            return None, None, f"⚠️ No players match the combined criteria. (Filtered {len(df)} → 0 players)"
        
        # Info text
        roles_enabled = [name for name, col in role_scores.items()]
        info_text = f"✅ Found {len(sorted_df)} players matching your criteria (Price: €{min_price:.0f}M-€{price_threshold:.0f}M, Age: {min_age}-{max_age}, Apps: ≥{min_apps})\n\nRoles: {', '.join(roles_enabled)}"
        
        return sorted_df, role_scores, info_text
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error in process_analysis: {e}")
        print(error_detail)
        return None, None, f"❌ Error processing data: {str(e)}"


def main():
    """Main Streamlit application."""
    
    # Title and header
    st.title("⚽ FM Scout Gem")
    st.markdown("### Advanced Football Manager Player Scout Tool")
    
    # Sidebar for filters
    with st.sidebar:
        st.header("📁 Upload & Filters")
        
        # File upload
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'], help="Upload your player statistics CSV file")
        
        if uploaded_file is None:
            st.info("👆 Please upload a CSV file to begin.")
            st.stop()
        
        # Read CSV
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"❌ Error reading CSV: {str(e)}")
            st.stop()
        
        st.divider()
        
        # Filter settings
        st.subheader("🔍 Filter Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            min_price = st.slider("Min Price (€M)", 0, 500, 0, 1)
            min_apps = st.slider("Min Apps", 0, 50, 0, 1)
            min_age = st.slider("Min Age", 16, 35, 17, 1)
        with col2:
            price_threshold = st.slider("Max Price (€M)", 1, 500, 200, 1)
            max_age = st.slider("Max Age", 17, 40, 30, 1)
        
        st.divider()
        
        # Position filters
        st.subheader("📍 Role Filters")
        
        include_coff = st.checkbox("Coff (Attacking Mid)", value=True)
        include_striker = st.checkbox("Striker", value=True)
        include_winger = st.checkbox("Winger", value=True)
        include_defensive_mid = st.checkbox("Defensive Mid", value=True)
        include_defenders = st.checkbox("Defenders (CB)", value=True)
        include_fullbacks = st.checkbox("Fullbacks", value=True)
        include_goalkeeper = st.checkbox("Goalkeeper", value=True)
        
        st.divider()
        
        analyze_btn = st.button("🔍 Analyze Players", use_container_width=True, type="primary")
    
    # Main content area
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
        st.session_state.sorted_df = None
        st.session_state.role_scores = None
    
    if analyze_btn or st.session_state.analyzed:
        # Process analysis
        sorted_df, role_scores, info_text = process_analysis(
            df, min_price, price_threshold, min_apps, max_age, min_age,
            include_coff, include_striker, include_winger, include_defenders,
            include_defensive_mid, include_fullbacks, include_goalkeeper
        )
        
        if sorted_df is None:
            st.markdown(f"<div class='info-box'>{info_text}</div>", unsafe_allow_html=True)
            st.stop()
        
        # Store results in session state
        st.session_state.analyzed = True
        st.session_state.sorted_df = sorted_df
        st.session_state.role_scores = role_scores
        
        # Display success info
        st.markdown(f"<div class='success-box'>{info_text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        
        # Prepare display DataFrame
        display_df = pd.DataFrame()
        display_df['Name'] = sorted_df['Name']
        display_df['Club'] = sorted_df['Club']
        display_df['Age'] = sorted_df['_age']
        display_df['Guide Value'] = sorted_df.apply(lambda row: f"€{row['_price']/1_000_000:.1f}M", axis=1)
        display_df['Value Index'] = sorted_df['Value Index'].round(2)
        display_df['Age Factor'] = sorted_df['Age Factor'].round(2)
        
        # Add role-specific scores
        for role_name, score_col in role_scores.items():
            if score_col in sorted_df.columns:
                display_name = role_name.replace('_', ' ').title()
                display_df[display_name] = sorted_df[score_col].round(2)
        
        # Display main results table
        st.subheader("📊 Top Players by Value Index")
        st.dataframe(
            display_df.head(20),
            use_container_width=True,
            hide_index=False,
            column_config={
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Club": st.column_config.TextColumn("Club", width="medium"),
                "Age": st.column_config.NumberColumn("Age", format="%d"),
                "Guide Value": st.column_config.TextColumn("Value", width="small"),
                "Value Index": st.column_config.NumberColumn("Value Index", format="%.2f"),
                "Age Factor": st.column_config.NumberColumn("Age Factor", format="%.2f"),
            }
        )
        
        # Display all results (not just top 20)
        with st.expander(f"📋 View All {len(sorted_df)} Players"):
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=False,
                column_config={
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Club": st.column_config.TextColumn("Club", width="medium"),
                    "Age": st.column_config.NumberColumn("Age", format="%d"),
                    "Guide Value": st.column_config.TextColumn("Value", width="small"),
                    "Value Index": st.column_config.NumberColumn("Value Index", format="%.2f"),
                    "Age Factor": st.column_config.NumberColumn("Age Factor", format="%.2f"),
                }
            )
        
        # Leaderboards section - click to sort
        st.divider()
        st.subheader("🏆 Statistics Leaders - Click column headers to sort")
        
        # Create tabs for each role
        tabs = []
        tab_names = []
        
        if 'coff' in role_scores:
            tab_names.append("COFF")
        if 'strika' in role_scores:
            tab_names.append("Striker")
        if 'winger' in role_scores:
            tab_names.append("Winger")
        if 'defensive_mid' in role_scores:
            tab_names.append("Def Mid")
        if 'defenders' in role_scores:
            tab_names.append("Defender")
        if 'fullbacks' in role_scores:
            tab_names.append("Fullback")
        if 'goalkeeper' in role_scores:
            tab_names.append("GK")
        
        if tab_names:
            tabs = st.tabs(tab_names)
            
            tab_idx = 0
            
            if 'coff' in role_scores:
                with tabs[tab_idx]:
                    score_col = role_scores['coff']
                    leaderboard_df = sorted_df.sort_values(score_col, ascending=False)[['Name', 'Club', '_age', score_col]].head(20).reset_index(drop=True)
                    leaderboard_df.columns = ['Name', 'Club', 'Age', 'COFF Score']
                    st.dataframe(leaderboard_df, use_container_width=True, hide_index=False)
                tab_idx += 1
            
            if 'strika' in role_scores:
                with tabs[tab_idx]:
                    score_col = role_scores['strika']
                    leaderboard_df = sorted_df.sort_values(score_col, ascending=False)[['Name', 'Club', '_age', score_col]].head(20).reset_index(drop=True)
                    leaderboard_df.columns = ['Name', 'Club', 'Age', 'Striker Score']
                    st.dataframe(leaderboard_df, use_container_width=True, hide_index=False)
                tab_idx += 1
            
            if 'winger' in role_scores:
                with tabs[tab_idx]:
                    score_col = role_scores['winger']
                    leaderboard_df = sorted_df.sort_values(score_col, ascending=False)[['Name', 'Club', '_age', score_col]].head(20).reset_index(drop=True)
                    leaderboard_df.columns = ['Name', 'Club', 'Age', 'Winger Score']
                    st.dataframe(leaderboard_df, use_container_width=True, hide_index=False)
                tab_idx += 1
            
            if 'defensive_mid' in role_scores:
                with tabs[tab_idx]:
                    score_col = role_scores['defensive_mid']
                    leaderboard_df = sorted_df.sort_values(score_col, ascending=False)[['Name', 'Club', '_age', score_col]].head(20).reset_index(drop=True)
                    leaderboard_df.columns = ['Name', 'Club', 'Age', 'Def Mid Score']
                    st.dataframe(leaderboard_df, use_container_width=True, hide_index=False)
                tab_idx += 1
            
            if 'defenders' in role_scores:
                with tabs[tab_idx]:
                    score_col = role_scores['defenders']
                    leaderboard_df = sorted_df.sort_values(score_col, ascending=False)[['Name', 'Club', '_age', score_col]].head(20).reset_index(drop=True)
                    leaderboard_df.columns = ['Name', 'Club', 'Age', 'Defender Score']
                    st.dataframe(leaderboard_df, use_container_width=True, hide_index=False)
                tab_idx += 1
            
            if 'fullbacks' in role_scores:
                with tabs[tab_idx]:
                    score_col = role_scores['fullbacks']
                    leaderboard_df = sorted_df.sort_values(score_col, ascending=False)[['Name', 'Club', '_age', score_col]].head(20).reset_index(drop=True)
                    leaderboard_df.columns = ['Name', 'Club', 'Age', 'Fullback Score']
                    st.dataframe(leaderboard_df, use_container_width=True, hide_index=False)
                tab_idx += 1
            
            if 'goalkeeper' in role_scores:
                with tabs[tab_idx]:
                    score_col = role_scores['goalkeeper']
                    leaderboard_df = sorted_df.sort_values(score_col, ascending=False)[['Name', 'Club', '_age', score_col]].head(20).reset_index(drop=True)
                    leaderboard_df.columns = ['Name', 'Club', 'Age', 'GK Score']
                    st.dataframe(leaderboard_df, use_container_width=True, hide_index=False)
                tab_idx += 1
    
    # How to use section
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        ### Steps:
        1. **Upload CSV** - Upload your player statistics file (must include Name, Club, Age, Guide Value columns)
        2. **Set Filters** - Adjust price range, age, and minimum appearances in the sidebar
        3. **Toggle Roles** - Enable/disable role filters to apply specific coefficients
        4. **Click Analyze** - Generate the scout report
        
        ### Features:
        - **Sortable tables**: Click on any column header to sort ascending/descending
        - **Dark mode UI** for comfortable viewing
        - **Value Index calculation** based on performance vs price
        - **Role-specific scoring** with correct coefficients
        - **Interactive leaderboards** for each position
        """)


if __name__ == "__main__":
    main()
