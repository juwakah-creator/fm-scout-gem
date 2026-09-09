#!/usr/bin/env python3
"""Esempio completo: Toggle Gradio per Filtro Età Minima (min_age).

Questo script dimostra l'uso di un toggle Gradio per filtrare giocatori
in base all'età minima, con integrazione nella pipeline scout_app esistente.
"""

import gradio as gr
import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CARICAMENTO DATI
# ============================================================================

def load_sample_data(csv_path=None):
    """Carica i dati di esempio da CSV o genera dati mock.
    
    Args:
        csv_path: Percorso opzionale al file CSV. Se None, usa sample_players.csv
        
    Returns:
        pandas.DataFrame con i dati dei giocatori
    """
    if csv_path is None:
        csv_path = Path(__file__).parent / "sample_players.csv"
    
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Caricati {len(df)} giocatori da {csv_path}")
        return df
    except Exception as e:
        logger.warning(f"Impossibile leggere CSV: {e}. Uso dati mock.")
        return _generate_mock_data()

def _generate_mock_data():
    """Genera dati di esempio per test immediato."""
    sample_data = {
        'Name': [
            'Kylian Mbappé', 'Erling Haaland', 'Jude Bellingham',
            'Cole Palmer', 'Wonderkid Striker', 'Hidden Gem',
            'Bargain Forward', 'Veteran Player', 'Two-Way Warrior',
            'Segna Pressa', 'Crea Pressa', 'Finalizzatore Inter',
            'Creatore City', 'Pressatore Dortmund', 'Offensivo Real',
            'Bilanciato Juve', 'Da Sviluppare Napoli', 'Young Prospect',
            'Hidden Talent'
        ],
        'Age': [25, 23, 20, 21, 18, 22, 19, 32, 24, 22, 23, 21, 24, 20, 22, 25, 18, 19, 21],
        'Position': ['FW', 'FW', 'MF', 'FW', 'FW', 'DF', 'FW', 'MF', 'MF', 'DF', 'MF', 'FW', 'MF', 'MF', 'FW', 'MF', 'GK', 'FW', 'DF'],
        'Guide Value': ['€120M', '€150M', '€110M', '€65M', '€2.5M', '€4.0M', '€3.0M', '€1.0M', '€45M', '€35M', '€40M', '€30M', '€50M', '€20M', '€25M', '€15M', '€5M', '€8M', '€6M']
    }
    return pd.DataFrame(sample_data)

# ============================================================================
# FUNZIONI DI FILTRO (Integrate con scout_app.py)
# ============================================================================

def filter_by_min_age(enable_filter, min_age, df):
    """Funzione callback per il filtro età minima.
    
    Args:
        enable_filter: bool - Se True applica il filtro, altrimenti restituisce tutti i giocatori
        min_age: int - Età minima da filtrare
        df: pandas.DataFrame con i dati dei giocatori
        
    Returns:
        tuple: (df_filtrato, summary_html, status_msg)
    """
    if not enable_filter:
        # Filtro disabilitato: restituisci tutti i dati
        logger.info(f"Filtro età DISABILITATO - mostra tutti i {len(df)} giocatori")
        return df, _generate_summary_html(None, len(df), len(df)), "⚪ Filtro età **disabilitato** - mostra tutti i giocatori"
    
    # Filtro abilitato: applica il filtro
    if 'Age' not in df.columns:
        logger.error("Colonna 'Age' non trovata nel DataFrame")
        return df, _generate_error_html("Colonna 'Age' non disponibile"), "❌ Errore: colonna Age non trovata"
    
    # Validazione range età
    min_age = max(16, min(45, int(min_age)))
    df_filtered = df[df['Age'] >= min_age].copy()
    
    reduction_pct = ((len(df) - len(df_filtered)) / len(df) * 100) if len(df) > 0 else 0
    
    logger.info(f"Filtro età MINIMA attivo: min_age={min_age}, trovati {len(df_filtered)} giocatori (riduzione {reduction_pct:.1f}%)")
    
    summary = _generate_summary_html(min_age, len(df_filtered), len(df), reduction_pct)
    status = f"✅ Filtro età **MINIMA** attivo - Età minima: **{min_age}** anni - Giocatori trovati: **{len(df_filtered)}**"
    
    return df_filtered, summary, status

def filter_by_max_age(enable_filter, max_age, df):
    """Funzione callback per il filtro età massima.
    
    Args:
        enable_filter: bool - Se True applica il filtro
        max_age: int - Età massima da filtrare
        df: pandas.DataFrame con i dati dei giocatori
        
    Returns:
        tuple: (df_filtrato, summary_html, status_msg)
    """
    if not enable_filter:
        logger.info(f"Filtro età MAX disabilitato - mostra tutti i {len(df)} giocatori")
        return df, _generate_summary_html(None, len(df), len(df)), "⚪ Filtro età MAX **disabilitato**"
    
    max_age = max(16, min(45, int(max_age)))
    df_filtered = df[df['Age'] <= max_age].copy()
    
    reduction_pct = ((len(df) - len(df_filtered)) / len(df) * 100) if len(df) > 0 else 0
    
    logger.info(f"Filtro età MAX attivo: max_age={max_age}, trovati {len(df_filtered)} giocatori")
    
    summary = _generate_summary_html(max_age, len(df_filtered), len(df), reduction_pct, filter_type="MAX")
    status = f"✅ Filtro età **MAX** attivo - Età massima: **{max_age}** anni - Giocatori trovati: **{len(df_filtered)}**"
    
    return df_filtered, summary, status

def filter_by_age_range(enable_filter, min_age, max_age, df):
    """Funzione callback per il filtro età con range (min e max).
    
    Args:
        enable_filter: bool - Se True applica il filtro
        min_age: int - Età minima
        max_age: int - Età massima
        df: pandas.DataFrame con i dati dei giocatori
        
    Returns:
        tuple: (df_filtrato, summary_html, status_msg)
    """
    if not enable_filter:
        logger.info(f"Filtro range età disabilitato - mostra tutti i {len(df)} giocatori")
        return df, _generate_summary_html(None, len(df), len(df)), "⚪ Filtro range età **disabilitato**"
    
    min_age = max(16, min(45, int(min_age)))
    max_age = max(16, min(45, int(max_age)))
    
    # Assicuriamoci che min_age <= max_age
    if min_age > max_age:
        min_age, max_age = max_age, min_age
    
    df_filtered = df[(df['Age'] >= min_age) & (df['Age'] <= max_age)].copy()
    
    reduction_pct = ((len(df) - len(df_filtered)) / len(df) * 100) if len(df) > 0 else 0
    
    logger.info(f"Filtro range età attivo: [{min_age}, {max_age}], trovati {len(df_filtered)} giocatori")
    
    summary = _generate_summary_html_range(min_age, max_age, len(df_filtered), len(df), reduction_pct)
    status = f"✅ Filtro **range età** attivo - Range: [{min_age}, {max_age}] anni - Giocatori trovati: **{len(df_filtered)}**"
    
    return df_filtered, summary, status

# ============================================================================
# FUNZIONI DI UTILITÀ PER HTML
# ============================================================================

def _generate_summary_html(min_age, count_found, count_total, reduction_pct=None, filter_type="MIN"):
    """Genera HTML di riepilogo per il filtro età."""
    if min_age is None:
        return """
        <div style='padding: 15px; background: #fff3e0; border-radius: 8px; margin: 10px 0;'>
            <h4>⚪ Filtro età disabilitato</h4>
            <p><strong>Tutti i giocatori:</strong> {}</p>
        </div>
        """.format(count_total)
    
    if reduction_pct is None:
        reduction_pct = ((count_total - count_found) / count_total * 100) if count_total > 0 else 0
    
    return """
    <div style='padding: 15px; background: #e8f5e9; border-radius: 8px; margin: 10px 0;'>
        <h4>✅ Filtro età {} attivo</h4>
        <p><strong>Età minima:</strong> {} anni</p>
        <p><strong>Giocatori trovati:</strong> {} / {}</p>
        <p><strong>Riduzione:</strong> {:.1f}%</p>
    </div>
    """.format(filter_type, min_age, count_found, count_total, reduction_pct)

def _generate_summary_html_range(min_age, max_age, count_found, count_total, reduction_pct):
    """Genera HTML di riepilogo per il filtro range età."""
    return """
    <div style='padding: 15px; background: #e3f2fd; border-radius: 8px; margin: 10px 0;'>
        <h4>✅ Filtro range età attivo</h4>
        <p><strong>Range:</strong> [{} - {}] anni</p>
        <p><strong>Giocatori trovati:</strong> {} / {}</p>
        <p><strong>Riduzione:</strong> {:.1f}%</p>
    </div>
    """.format(min_age, max_age, count_found, count_total, reduction_pct)

def _generate_error_html(error_msg):
    """Genera HTML di errore."""
    return """
    <div style='padding: 15px; background: #ffebee; border-radius: 8px; margin: 10px 0;'>
        <h4>❌ Errore</h4>
        <p>{}</p>
    </div>
    """.format(error_msg)

# ============================================================================
# INTERFACCIA GRADIO
# ============================================================================

def create_demo():
    """Crea l'interfaccia Gradio completa con toggle età."""
    
    # Carica dati
    df = load_sample_data()
    
    with gr.Blocks(title="Toggle Età Minima - FM Scout Gem") as demo:
        gr.Markdown("""
        ## 🎯 Toggle Filtro Età Minima (min_age)
        
        Esempio completo di integrazione con la pipeline **FM Scout Gem**.
        Usa i checkbox per abilitare/disabilitare i filtri e gli slider per regolare i parametri.
        """)
        
        # Layout principale
        with gr.Row():
            # Pannello controlli (sinistra)
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Controlli Filtro")
                
                # Sezione 1: Filtro Età Minima
                with gr.Accordion("Filtro Età MINIMA", open=True):
                    gr.Markdown("### 🎯 Filtro Età MINIMA")
                    enable_min = gr.Checkbox(
                        value=True,
                        label="Abilita filtro età minima"
                    )
                    min_age_slider = gr.Slider(
                        minimum=16,
                        maximum=45,
                        value=20,
                        step=1,
                        label="Età minima (anni)"
                    )
                
                # Sezione 2: Filtro Età Massima
                with gr.Column():
                    enable_max = gr.Checkbox(
                        value=False,
                        label="Abilita filtro età massima"
                    )
                    max_age_slider = gr.Slider(
                        minimum=16,
                        maximum=45,
                        value=25,
                        step=1,
                        label="Età massima (anni)"
                    )
                
                # Sezione 3: Filtro Range Età
                with gr.Accordion("Filtro Range Età", open=False):
                    enable_range = gr.Checkbox(
                        value=False,
                        label="Abilita filtro range età"
                    )
                    with gr.Row():
                        range_min_slider = gr.Slider(
                            minimum=16,
                            maximum=45,
                            value=18,
                            step=1,
                            label="Età minima range"
                        )
                        range_max_slider = gr.Slider(
                            minimum=16,
                            maximum=45,
                            value=25,
                            step=1,
                            label="Età massima range"
                        )
                
                # Sezione 4: Rice Range (milioni)
                with gr.Accordion("Rice Range (milioni)", open=False):
                    rice_range_slider = gr.Slider(
                        minimum=0,
                        maximum=100,
                        value=50,
                        step=1,
                        label="Rice Range"
                    )
                
                # Sezione 5: Min Price (milioni)
                with gr.Accordion("Min Price (milioni)", open=False):
                    min_price_slider = gr.Slider(
                        minimum=0,
                        maximum=100,
                        value=50,
                        step=1,
                        label="Min Price"
                    )
                
                # Sezione 6: Minimum Player Guide Value
                with gr.Accordion("Minimum Player Guide Value", open=False):
                    guide_value_slider = gr.Slider(
                        minimum=0,
                        maximum=100,
                        value=50,
                        step=1,
                        label="Player Guide Value"
                    )
                
                
                # Sezione 8: Min Appearances
                with gr.Accordion("Min Appearances", open=False):
                    min_appearances_slider = gr.Slider(
                        minimum=0,
                        maximum=10,
                        value=0,
                        step=1,
                        label="Min Appearances"
                    )
                
                # Pulsanti di azione
                with gr.Row():
                    btn_apply = gr.Button("🔄 Applica Filtri", variant="primary", size="sm")
                    btn_reset = gr.Button("↩️ Reset", variant="secondary", size="sm")
            
            # Pannello risultati (destra)
            with gr.Column(scale=2):
                gr.Markdown("### 📋 Risultati Filtraggio")
                results_df = gr.Dataframe(label="Giocatori Filtrati", interactive=False)
                summary_md = gr.Markdown(value="**Attendi modifiche ai filtri...**")
                status_md = gr.Markdown(value="⚪ Nessun filtro attivo - mostra tutti i giocatori")
                
                # Tabella originale per confronto
                with gr.Tab("Dati Originali"):
                    original_df = gr.Dataframe(label="Dati Originali", interactive=False)
                
                # ====================================================================
                # CONNESSIONE EVENTI (dentro il contesto gr.Blocks)
                # ====================================================================
                
                # Evento 1: Cambio checkbox età minima
                enable_min.change(
                    fn=filter_by_min_age,
                    inputs=[enable_min, min_age_slider, original_df],
                    outputs=[results_df, summary_md, status_md]
                )
                
                # Evento 2: Cambio slider età minima
                min_age_slider.change(
                    fn=filter_by_min_age,
                    inputs=[enable_min, min_age_slider, original_df],
                    outputs=[results_df, summary_md, status_md]
                )
                
                # Evento 3: Cambio checkbox età massima
                enable_max.change(
                    fn=filter_by_max_age,
                    inputs=[enable_max, max_age_slider, original_df],
                    outputs=[results_df, summary_md, status_md]
                )
                
                # Evento 4: Cambio slider età massima
                max_age_slider.change(
                    fn=filter_by_max_age,
                    inputs=[enable_max, max_age_slider, original_df],
                    outputs=[results_df, summary_md, status_md]
                )
                
                # Evento 5: Cambio checkbox range età
                enable_range.change(
                    fn=filter_by_age_range,
                    inputs=[enable_range, range_min_slider, range_max_slider, original_df],
                    outputs=[results_df, summary_md, status_md]
                )
                
                # Evento 6: Cambio slider range età
                range_min_slider.change(
                    fn=filter_by_age_range,
                    inputs=[enable_range, range_min_slider, range_max_slider, original_df],
                    outputs=[results_df, summary_md, status_md]
                )
                range_max_slider.change(
                    fn=filter_by_age_range,
                    inputs=[enable_range, range_min_slider, range_max_slider, original_df],
                    outputs=[results_df, summary_md, status_md]
                )
                
                # Evento 7: Pulsante applica (per applicare tutti i filtri attivi)
                def apply_all_filters(enable_min, min_age, enable_max, max_age, enable_range, range_min, range_max, rice_range, min_price, guide_value, min_appearances, df):
                    """Applica tutti i filtri attivi contemporaneamente."""
                    result_df = df.copy()
                    active_filters = []
                    
                    if enable_min:
                        result_df = result_df[result_df['Age'] >= min_age]
                        active_filters.append(f"min_age={min_age}")
                    
                    if enable_max:
                        result_df = result_df[result_df['Age'] <= max_age]
                        active_filters.append(f"max_age={max_age}")
                    
                    if enable_range:
                        result_df = result_df[(result_df['Age'] >= range_min) & (result_df['Age'] <= range_max)]
                        active_filters.append(f"range[{range_min}-{range_max}]")
                    
                    # Aggiungi nuovi filtri se abilitati (per ora solo come info)
                    if rice_range > 0:
                        active_filters.append(f"rice_range={rice_range}")
                    if min_price > 0:
                        active_filters.append(f"min_price={min_price}")
                    if guide_value > 0:
                        active_filters.append(f"guide_value={guide_value}")
                    if min_appearances > 0:
                        active_filters.append(f"min_appearances={min_appearances}")
                    
                    if not active_filters:
                        summary = _generate_summary_html(None, len(result_df), len(df))
                        status = "⚪ Nessun filtro attivo - mostra tutti i giocatori"
                    else:
                        reduction_pct = ((len(df) - len(result_df)) / len(df) * 100) if len(df) > 0 else 0
                        summary = f"""
                        <div style='padding: 15px; background: #c8e6c9; border-radius: 8px; margin: 10px 0;'>
                            <h4>✅ Filtri attivi: {', '.join(active_filters)}</h4>
                            <p><strong>Giocatori trovati:</strong> {len(result_df)} / {len(df)}</p>
                            <p><strong>Riduzione:</strong> {reduction_pct:.1f}%</p>
                        </div>
                        """
                        status = f"✅ Filtri combinati applicati: {', '.join(active_filters)}"
                    
                    return result_df, summary, status
                
                btn_apply.click(
                    fn=apply_all_filters,
                    inputs=[enable_min, min_age_slider, enable_max, max_age_slider,
                            enable_range, range_min_slider, range_max_slider,
                            rice_range_slider, min_price_slider, guide_value_slider,
                            min_appearances_slider, original_df],
                    outputs=[results_df, summary_md, status_md]
                )
                
                # Evento 8: Pulsante reset
                def reset_filters(df):
                    """Resetta tutti i filtri e mostra i dati originali."""
                    return df, _generate_summary_html(None, len(df), len(df)), "⚪ Filtri resettati - mostra tutti i giocatori"
                
                btn_reset.click(
                    fn=reset_filters,
                    inputs=original_df,
                    outputs=[results_df, summary_md, status_md]
                )
                
                # Popola la tabella originale all'avvio
                demo.load(
                    fn=lambda df: (df, _generate_summary_html(None, len(df), len(df)), "⚪ Nessun filtro attivo - mostra tutti i giocatori"),
                    inputs=original_df,
                    outputs=[results_df, summary_md, status_md]
                )
    
    return demo

# ============================================================================
# INTEGRAZIONE CON SCOUT_APP.PY (Pipeline esistente)
# ============================================================================

def integrate_with_scout_app():
    """Funzione per integrare il toggle con la pipeline scout_app esistente.
    
    Questa funzione mostra come estendere scout_app.py per supportare
    il filtro età tramite Gradio.
    """
    try:
        from scout_app import parse_value, normalize, age_factor
        
        # Esempio di integrazione: usa le funzioni di scout_app per calcolare
        # il Value Index e poi applica il filtro età
        df = load_sample_data()
        
        # Simula il processo di scouting
        df['Guide Value Numeric'] = df['Guide Value'].apply(parse_value)
        df['Age Factor'] = df['Age'].apply(age_factor)
        
        logger.info(f"Integrazione con scout_app.py: {len(df)} giocatori processati")
        return df
    except ImportError:
        logger.warning("scout_app.py non trovato, uso dati mock")
        return _generate_mock_data()

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Toggle Età Minima - FM Scout Gem")
    parser.add_argument('--host', default='0.0.0.0', help='Indirizzo server')
    parser.add_argument('--port', type=int, default=7860, help='Porta server')
    parser.add_argument('--csv', help='Percorso file CSV personalizzato')
    parser.add_argument('--debug', action='store_true', help='Attiva debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    logger.info(f"Avvio applicazione Toggle Età - Host: {args.host}, Porta: {args.port}")
    
    # Crea e avvia l'applicazione
    demo = create_demo()
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        show_error=True
    )
