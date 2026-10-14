#!/usr/bin/env python3
"""Football Manager Scout Application - Main Entry Point

This module provides the main application interface for scouting players in Football Manager.
It uses Gradio for the web UI and connects to scout_app.py for analysis logic.
"""

import gradio as gr
import pandas as pd
import numpy as np
from scout_app import detect_columns, parse_value, normalize, calculate_tactical_dimensions, age_factor

# Import role-specific scoring functions
from cof import calculate_cof_score
from strika import calculate_striker_score
from goalkeeper import calculate_goalkeeper_score
from defensive_mid import calculate_defensive_score
from defenders import calculate_defender_score
from fullbacks import calculate_fullback_score
from winger import calculate_offensive_score

# Dark mode CSS with scrollable tables support
DARK_MODE_CSS = """
.gradio-container {
    background-color: #0d1117 !important;
}
.main {
    background-color: #161b22 !important;
}
.block-title {
    color: #58a6ff !important;
}
"""

# CSS for scrollable table containers and sortable tables
TABLE_CSS = """
/* Scrollable container for wide tables */
.scrollable-table-container {
    overflow-x: auto;
    max-width: 100%;
    -webkit-overflow-scrolling: touch;
}

/* Ensure tables are responsive */
.table-responsive {
    width: 100%;
    min-width: 100%;
}

/* Custom scrollbar styling for dark theme */
.scrollable-table-container::-webkit-scrollbar {
    height: 8px;
}
.scrollable-table-container::-webkit-scrollbar-track {
    background: #21262d;
    border-radius: 4px;
}
.scrollable-table-container::-webkit-scrollbar-thumb {
    background: #30363d;
    border-radius: 4px;
}
.scrollable-table-container::-webkit-scrollbar-thumb:hover {
    background: #58a6ff;
}

/* Table styling for dark theme */
.custom-table table {
    width: 100% !important;
    min-width: 100% !important;
    border-collapse: collapse;
}
.custom-table th {
    background-color: #0d1117 !important;
    color: #58a6ff !important;
    font-weight: bold !important;
    border: 1px solid #30363d !important;
    padding: 8px 12px !important;
    white-space: nowrap !important;
    cursor: pointer !important;
    user-select: none !important;
}
.custom-table th:hover {
    background-color: #1f2937 !important;
}
.custom-table th.sort-asc::after {
    content: " ▲";
    font-size: 10px;
}
.custom-table th.sort-desc::after {
    content: " ▼";
    font-size: 10px;
}
.custom-table td {
    background-color: #161b22 !important;
    color: #f5f5f5 !important;
    border: 1px solid #30363d !important;
    padding: 8px 12px !important;
}
.custom-table tr:nth-child(even) td {
    background-color: #1a1a1a !important;
}
.custom-table tr:nth-child(odd) td {
    background-color: #0d1117 !important;
}

/* Info boxes */
.info-box {
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 14px;
    line-height: 1.5;
}
.info-box.info {
    background-color: #1a2535;
    border: 1px solid #58a6ff;
    color: #58a6ff;
}
.info-box.success {
    background-color: #14261a;
    border: 1px solid #3fb950;
    color: #3fb950;
}
"""

# JavaScript for sortable tables
SORTABLE_TABLE_JS = """
<script>
(function() {
    function makeTableSortable(table) {
        if (!table || table.dataset.sortable === 'true') return;
        table.dataset.sortable = 'true';
        
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            // Skip index column (first th)
            if (index === 0) return;
            
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const tbody = table.querySelector('tbody');
                if (!tbody) return;
                
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const isNumeric = !isNaN(rows[0]?.cells[index]?.innerText.replace(/[^0-9.-]/g, ''));
                
                // Toggle sort direction
                const currentAsc = header.classList.contains('sort-asc');
                const sortAsc = !currentAsc;
                
                // Remove sort classes from all headers
                headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                header.classList.add(sortAsc ? 'sort-asc' : 'sort-desc');
                
                // Sort rows
                rows.sort((a, b) => {
                    const aVal = a.cells[index]?.innerText.trim();
                    const bVal = b.cells[index]?.innerText.trim();
                    
                    if (isNumeric) {
                        const aNum = parseFloat(aVal.replace(/[^0-9.-]/g, '')) || 0;
                        const bNum = parseFloat(bVal.replace(/[^0-9.-]/g, '')) || 0;
                        return sortAsc ? aNum - bNum : bNum - aNum;
                    } else {
                        return sortAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                    }
                });
                
                // Re-append sorted rows
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    }
    
    // Make all tables sortable
    document.querySelectorAll('.custom-table table').forEach(makeTableSortable);
    
    // Also handle dynamically added tables
    const observer = new MutationObserver(() => {
        document.querySelectorAll('.custom-table table').forEach(makeTableSortable);
    });
    observer.observe(document.body, { childList: true, subtree: true });
})();
</script>
"""

def create_app():
    """Create the Gradio app with all components."""
    
    def process_analysis(csv_file, min_price=0.0, price_threshold=200.0, 
                         min_apps=10, max_age=30, min_age=17,
                         include_cof=True, include_striker=True,
                         include_winger=True, include_defenders=True,
                         include_defensive_mid=True, include_fullbacks=True,
                         include_goalkeeper=True):
        """Process uploaded CSV and analyze players based on filters.
        
        Args:
            csv_file: Path to the uploaded CSV file
            min_price: Minimum price in millions €
            price_threshold: Maximum price in millions €
            min_apps: Minimum appearances
            max_age: Maximum age
            min_age: Minimum age
            include_cof: Include attacking midfielders (cof)
            include_striker: Include strikers
            include_winger: Include wingers
            include_defenders: Include defenders
            include_defensive_mid: Include defensive midfielders
            include_fullbacks: Include fullbacks
            include_goalkeeper: Include goalkeepers
            
        Returns:
            tuple: (result_html, debug_html, info_text)
        """
        if csv_file is None:
            return "<div class='info-box info'>⚠️ Please upload a CSV file first.</div>", "", "No file uploaded"
        
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Detect columns automatically
            cm = detect_columns(df)
            
            # Parse Guide Value to numeric _price in €
            df['_price'] = df[cm['Guide Value']].apply(parse_value)
            df['_age'] = pd.to_numeric(df[cm['Age']], errors='coerce')
            df['_apps'] = pd.to_numeric(df[cm['Appearances']], errors='coerce')
            
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
                return "<div class='info-box info'>⚠️ No players match the criteria. Try adjusting filters.</div>", "", f"Filtered {len(df)} → 0 players"
            
            # Define available offensive stats - try to detect columns from the CSV
            available_off = {}
            df_columns_lower = [col.lower() for col in df.columns]
            
            offensive_candidates = {
                'Goal Contributions per 90': ['goal contributions p90', 'g+a p90', 'goal contributions per 90'],
                'xG per 90': ['xg p90', 'xG per 90', 'expected goals p90'],
                'xA per 90': ['xa p90', 'xA per 90'],
                'Shots on Target per 90': ['shots on target p90', 'sot p90'],
                'Key Passes per 90': ['key passes p90', 'kp p90'],
                'Attacking Actions per 90': ['attacking actions p90'],
                'NP-xG per 90': ['np-xg p90', 'non-penalty xg p90'],
                'xG Overperformance': ['xg overperformance'],
                'Shots per 90': ['shots p90', 'shots per 90']
            }
            
            for standard_name, variations in offensive_candidates.items():
                for variation in variations:
                    if variation.lower() in df_columns_lower:
                        available_off[standard_name] = df.columns[df_columns_lower.index(variation.lower())]
                        break
            
            # Calculate role-specific scores using correct coefficients
            role_scores = {}
            
            # COF (Attacking Mid) - calculate_cof_score from cof.py
            if include_cof:
                filtered_df['_cof_score'] = filtered_df.apply(calculate_cof_score, axis=1)
                role_scores['cof'] = '_cof_score'
            
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
                return "<div class='info-box info'>⚠️ No roles selected. Please enable at least one position filter.</div>", "", "No roles selected"
            
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
            
            # Sort by Value Index descending and take top 20
            sorted_df = filtered_df.sort_values('Value Index', ascending=False).head(20)
            
            if len(sorted_df) == 0:
                return "<div class='info-box info'>⚠️ No players match the combined criteria.</div>", "", f"Filtered {len(df)} → 0 players"
            
            # Build output DataFrame
            result_out = pd.DataFrame()
            result_out['Name'] = sorted_df['Name']
            result_out['Club'] = sorted_df['Club']
            result_out['Age'] = sorted_df['_age']
            result_out['Guide Value'] = df.loc[sorted_df.index, cm['Guide Value']]  # Original string values
            result_out['Value Index'] = sorted_df['Value Index']
            result_out['Age Factor'] = sorted_df['Age Factor']
            
            # Add role-specific scores
            for role_name, score_col in role_scores.items():
                if score_col in sorted_df.columns:
                    result_out[role_name] = sorted_df[score_col].round(2)
            
            # Create HTML table with scrollable container wrapper - include index as first column
            html_table = f"""<div class="scrollable-table-container">
<table class="custom-table">
{sorted_df.to_html(classes='', border=0, index=True)}
</table>
</div>"""
            
            # Debug info - also include index
            debug_df = sorted_df[['Name', 'Value Index']].copy()
            debug_df['Value Index'] = debug_df['Value Index'].round(2)
            debug_html = f"<div class='scrollable-table-container'><table>{debug_df.to_html(classes='custom-table', border=0, index=True)}</table></div>"
            
            # Info text
            roles_enabled = [name for name, col in role_scores.items()]
            info_text = f"✅ Found {len(sorted_df)} players matching your criteria (Price: €{min_price:.0f}M-€{price_threshold:.0f}M, Age: {min_age}-{max_age}, Apps: ≥{min_apps})\nRoles: {', '.join(roles_enabled)}"
            
            return html_table, debug_html, info_text, filtered_df, role_scores
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Error in process_analysis: {e}")
            print(error_detail)
            return f"<div class='info-box info'>❌ Error processing file: {str(e)}</div>", "", None, None, {}
    
    # Create the Gradio interface
    with gr.Blocks(title="FM Scout Gem - Football Manager Scout") as app:
        
        gr.Markdown("# ⚽ FM Scout Gem")
        gr.Markdown("### Advanced Football Manager Player Scout Tool")
        
        # State to store filtered dataframe for leaderboard feature
        filtered_df_state = gr.State(value=None)
        
        with gr.Row():
            # Left column for file upload and filters
            with gr.Column(scale=1):
                csv_input = gr.File(label="📁 Upload CSV", type="filepath")
                
                with gr.Group():
                    gr.Markdown("### 🔍 Filter Settings")
                    
                    with gr.Row():
                        min_price = gr.Slider(0, 500, value=0, step=1, label="Min Price (€M)")
                        price_threshold = gr.Slider(1, 500, value=200, step=1, label="Max Price (€M)")
                
                with gr.Row():
                    min_apps = gr.Slider(0, 50, value=0, step=1, label="Min Apps")
                    max_age = gr.Slider(17, 40, value=30, step=1, label="Max Age")
                
                with gr.Row():
                    min_age = gr.Slider(16, 35, value=17, step=1, label="Min Age")
                
                # Position filters - using role names matching .py files
                with gr.Group():
                    gr.Markdown("### 📍 Role Filters (Coefficients)")
                    
                    # Row 1: cof and strika
                    pos_row1 = gr.Row()
                    with pos_row1:
                        pos_cof = gr.Checkbox(value=True, label="CoF (Attacking Mid)")
                        pos_striker = gr.Checkbox(value=True, label="Striker")
                    
                    # Row 2: winger and defensive_mid
                    pos_row2 = gr.Row()
                    with pos_row2:
                        pos_winger = gr.Checkbox(value=True, label="Winger")
                        pos_defensive_mid = gr.Checkbox(value=True, label="Defensive Mid")
                    
                    # Row 3: defenders and fullbacks
                    pos_row3 = gr.Row()
                    with pos_row3:
                        pos_defenders = gr.Checkbox(value=True, label="Defenders (CB)")
                        pos_fullbacks = gr.Checkbox(value=True, label="Fullbacks")
                    
                    # Goalkeeper on its own line
                    pos_gk = gr.Checkbox(value=True, label="Goalkeeper")
                
                analyze_btn = gr.Button("🔍 Analyze Players", variant="primary", size="lg")
            
            # Right column for results
            with gr.Column(scale=3):
                result_output = gr.HTML(label="Results", value="<div class='info-box info'>Upload a CSV file and click Analyze to see results.</div>")
                debug_output = gr.HTML(label="Debug Info (Value Index)", value="")
        
        # Leaderboard section - clickable buttons for each stat category
        gr.Markdown("### 🏆 Statistic Leaders - Click on a table to see the top players")
        
        with gr.Row():
            leaderboard_cof = gr.HTML(label="CoF Leaders", value="<div class='info-box info'>Click Analyze first to see CoF leaders</div>")
            leaderboard_striker = gr.HTML(label="Striker Leaders", value="<div class='info-box info'>Click Analyze first to see Striker leaders</div>")
        
        with gr.Row():
            leaderboard_winger = gr.HTML(label="Winger Leaders", value="<div class='info-box info'>Click Analyze first to see Winger leaders</div>")
            leaderboard_defensive_mid = gr.HTML(label="Defensive Mid Leaders", value="<div class='info-box info'>Click Analyze first to see Defensive Mid leaders</div>")
        
        with gr.Row():
            leaderboard_defenders = gr.HTML(label="Defender Leaders", value="<div class='info-box info'>Click Analyze first to see Defender leaders</div>")
            leaderboard_fullbacks = gr.HTML(label="Fullback Leaders", value="<div class='info-box info'>Click Analyze first to see Fullback leaders</div>")
        
        with gr.Row():
            leaderboard_goalkeeper = gr.HTML(label="Goalkeeper Leaders", value="<div class='info-box info'>Click Analyze first to see Goalkeeper leaders</div>")
        
        # Hidden state to store all role scores data
        role_scores_state = gr.State(value={})
        
        # Event handlers - pass all checkbox states
        def update_leaderboards(filtered_df, role_scores):
            """Update all leaderboard tables based on filtered data."""
            if filtered_df is None or len(filtered_df) == 0:
                return ["<div class='info-box info'>No data available</div>"] * 7
            
            leaderboards = {}
            role_display_names = {
                'cof': ('CoF (Attacking Mid)', '_cof_score'),
                'strika': ('Striker', '_striker_score'),
                'winger': ('Winger', '_winger_score'),
                'defensive_mid': ('Defensive Mid', '_dm_score'),
                'defenders': ('Defender', '_def_score'),
                'fullbacks': ('Fullback', '_fb_score'),
                'goalkeeper': ('Goalkeeper', '_gk_score')
            }
            
            for role_key, (display_name, score_col) in role_display_names.items():
                if score_col in filtered_df.columns and len(filtered_df) > 0:
                    # Sort by this role's score and get top 10
                    sorted_by_role = filtered_df.sort_values(score_col, ascending=False).head(10)
                    
                    # Create leaderboard table
                    leaderboard_df = pd.DataFrame()
                    leaderboard_df['Rank'] = range(1, len(sorted_by_role) + 1)
                    leaderboard_df['Player'] = sorted_by_role['Name'].values
                    leaderboard_df['Club'] = sorted_by_role['Club'].values
                    leaderboard_df['Age'] = sorted_by_role['_age'].values
                    leaderboard_df[display_name] = sorted_by_role[score_col].round(2).values
                    
                    leaderboards[role_key] = f"""<div class="scrollable-table-container">
<table class="custom-table">
{leaderboard_df.to_html(classes='', border=0, index=False)}
</table>
</div>"""
                else:
                    leaderboards[role_key] = "<div class='info-box info'>Role not enabled or no data</div>"
            
            return [
                leaderboards.get('cof', "<div class='info-box info'>No data</div>"),
                leaderboards.get('strika', "<div class='info-box info'>No data</div>"),
                leaderboards.get('winger', "<div class='info-box info'>No data</div>"),
                leaderboards.get('defensive_mid', "<div class='info-box info'>No data</div>"),
                leaderboards.get('defenders', "<div class='info-box info'>No data</div>"),
                leaderboards.get('fullbacks', "<div class='info-box info'>No data</div>"),
                leaderboards.get('goalkeeper', "<div class='info-box info'>No data</div>")
            ]
        
        analyze_btn.click(
            fn=process_analysis,
            inputs=[csv_input, min_price, price_threshold, min_apps, max_age, min_age,
                    pos_cof, pos_striker, pos_winger, pos_defenders,
                    pos_defensive_mid, pos_fullbacks, pos_gk],
            outputs=[result_output, debug_output, filtered_df_state, role_scores_state]
        ).then(
            fn=update_leaderboards,
            inputs=[filtered_df_state, role_scores_state],
            outputs=[leaderboard_cof, leaderboard_striker, leaderboard_winger,
                     leaderboard_defensive_mid, leaderboard_defenders, leaderboard_fullbacks, 
                     leaderboard_goalkeeper]
        )
        
        # Example info
        with gr.Accordion("ℹ️ How to Use", open=False):
            gr.Markdown("""
            ### Steps:
            1. **Upload CSV** - Upload your player statistics file (must include Name, Club, Age, Guide Value columns)
            2. **Set Filters** - Adjust price range, age, and minimum appearances as needed
            3. **Toggle Roles** - Enable/disable role filters to apply specific coefficients
            4. **Click Analyze** - Generate the scout report
            
            ### Roles Available:
            - **CoF**: Attacking Midfielder (coefficients from cof.py)
            - **Striker**: Striker (coefficients from strika.py)
            - **Winger**: Winger/Wide midfielder (coefficients from winger.py)
            - **Defensive Mid**: Defensive Midfielder (coefficients from defensive_mid.py)
            - **Defenders**: Center Backs (coefficients from defenders.py)
            - **Fullbacks**: Fullbacks (coefficients from fullbacks.py)
            - **Goalkeeper**: Goalkeeper (coefficients from goalkeeper.py)
            
            ### Features:
            - Horizontal scrollable tables for all advanced stats
            - Dark mode UI for comfortable viewing
            - Value Index calculation based on performance vs price
            - Role-specific scoring with correct coefficients
            - **Index column** visible in all statistics tables
            - **Sortable tables**: Click on any column header to sort ascending/descending
            """)
    
    return app

def launch_app():
    """Launch the Gradio application."""
    app = create_app()
    app.queue().launch(
        server_name="127.0.0.1",
        server_port=7861,
        show_error=True,
        share=False,
        css=DARK_MODE_CSS + TABLE_CSS,
        head=SORTABLE_TABLE_JS
    )

if __name__ == "__main__":
    launch_app()
