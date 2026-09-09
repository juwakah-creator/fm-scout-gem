# Guida Tecnica: Slider Gradio per Filtro Età Minima (min_age)

## 1. Struttura del Componente Gradio

### 1.1 Import e Configurazione Base

```python
import gradio as gr
import pandas as pd
import numpy as np
```

### 1.2 Layout Responsive con Row/Column

Il layout utilizza `gr.Row` per organizzare i componenti in righe orizzontali e `gr.Column` per raggruppare controlli correlati:

```python
with gr.Blocks(title="Football Scout - Filtro Età") as demo:
    gr.Markdown("## Filtro Età Minima con Slider Gradio")
    
    with gr.Row():
        # Colonna sinistra: slider e info
        with gr.Column(scale=1):
            min_age_slider = gr.Slider(
                minimum=16,
                maximum=45,
                value=18,
                step=1,
                label="Età minima (anni)",
                info="Filtra giocatori con età >= valore selezionato"
            )
        
        # Colonna destra: risultati
        with gr.Column(scale=2):
            age_info = gr.Markdown("### Informazioni Filtro")
            results_output = gr.Dataframe(label="Giocatori Filtrati")
```

### 1.3 Componenti Chiave

| Componente | Parametri | Scopo |
|------------|-----------|-------|
| `gr.Slider` | `minimum`, `maximum`, `value`, `step` | Imposta età minima (range 16-45, default 18) |
| `gr.Row` | `scale` (opzionale) | Layout orizzontale responsive |
| `gr.Column` | `scale` (opzionale) | Raggruppa componenti correlati |

---

## 2. Integrazione con Pipeline Hugging Face / Scout App

### 2.1 Funzione di Processing con Filtro Età Minima

```python
def process_with_min_age_filter(df, min_age):
    """Processa i dati applicando il filtro età minima.
    
    Args:
        df: DataFrame con i dati dei giocatori
        min_age: int - Età minima da filtrare
        
    Returns:
        Tuple: (df_filtrato, html_riepilogo)
    """
    if df is None or len(df) == 0:
        return df, "<p>Nessun dato disponibile</p>"
    
    # Copia per non modificare il DataFrame originale
    df_processed = df.copy()
    
    # Assicurati che l'età sia numerica
    if 'Age' in df_processed.columns:
        df_processed['_age_clean'] = pd.to_numeric(df_processed['Age'], errors='coerce')
    else:
        # Cerca colonne simili
        age_cols = [c for c in df_processed.columns if 'age' in c.lower()]
        if age_cols:
            df_processed['_age_clean'] = pd.to_numeric(df_processed[age_cols[0]], errors='coerce')
        else:
            return df, "<p>Colonna età non trovata</p>"
    
    # Applica il filtro età minima
    df_filtered = df_processed[df_processed['_age_clean'] >= min_age].copy()
    
    # Genera riepilogo
    filtered_count = len(df_filtered)
    original_count = len(df_processed)
    html_summary = f"""
    <div style='padding: 10px; background: #f0f0f0; border-radius: 5px;'>
        <h4>📊 Risultato Filtro Età</h4>
        <p><strong>Età minima selezionata:</strong> {min_age} anni</p>
        <p><strong>Giocatori originali:</strong> {original_count}</p>
        <p><strong>Giocatori dopo filtro:</strong> {filtered_count}</p>
        <p><strong>Riduzione:</strong> {((original_count - filtered_count) / original_count * 100):.1f}%</p>
    </div>
    """
    
    return df_filtered, html_summary
```

### 2.2 Integrazione con Pipeline Esistente (app.py style)

```python
def process_analysis_with_min_age(df, mode, min_age, 
                                   min_price_val, price_val, min_apps, max_age):
    """Versione estesa che integra il filtro min_age nella pipeline esistente.
    
    Args:
        df: DataFrame contenente i dati dei giocatori
        mode: Modalità analisi - "winger", "defensive_mid", o "coff"
        min_age: int - Età minima (filtro sempre applicato)
        min_price_val: float - Prezzo minimo in milioni
        price_val: float - Prezzo massimo in milioni
        min_apps: int - Presenze minime
        max_age: int - Età massima (filtro esistente)
        
    Returns:
        Tuple: (result_html, debug_html)
    """
    if df is None or len(df) == 0:
        return "<p>No data available</p>", "<p>No data available</p>"
    
    valid_modes = ["winger", "defensive_mid", "coff"]
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Valid modes are: {valid_modes}")
    
    result_html = ""
    debug_html = ""
    
    try:
        cm = detect_columns(df)
        df_processed = df.copy()
        
        # Conversione valori
        df_processed['_price'] = df_processed[cm['Guide Value']].apply(parse_value)
        df_processed['_age'] = pd.to_numeric(df_processed[cm['Age']], errors='coerce')
        df_processed['_apps'] = pd.to_numeric(df_processed[cm['Appearances']], errors='coerce')
        
        # Conversione statistiche in numerico
        all_stat_cols = [
            'Goal Contributions per 90', 'xG per 90', 'xA per 90', 'NP-xG per 90',
            'Shots on Target per 90', 'Key Passes per 90', 'Attacking Actions per 90',
            'Dribbling completati per 90', 'Passaggi progressivi per 90', 'Cross riusciti per 90',
            'xG Overperformance', 'Shots per 90',
            'Tackles per 90', 'Interceptions per 90', 'Progressive Passes per 90',
            'Pressures Attempted per 90', 'Possession Won per 90', 'Header Win %',
            'Pass Completion %', 'Average Rating'
        ]
        for col in all_stat_cols:
            if col in df_processed.columns:
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
        
        # Filtri prezzo e presenze (sempre applicati)
        min_price_euros = min_price_val * 1_000_000
        max_price_euros = price_val * 1_000_000
        
        # Costruzione filtro età: combinato min_age E max_age
        age_mask = (df_processed['_age'] >= min_age) & \
                   (df_processed['_age'] < max_age) & \
                   (df_processed['_age'].notna())
        
        filtered_df = df_processed[
            (df_processed['_price'] >= min_price_euros) &
            (df_processed['_price'] <= max_price_euros) &
            (df_processed['_apps'] >= min_apps) &
            age_mask
        ].copy()
        
        # ... resto della pipeline esistente ...
        
    except Exception as e:
        result_html = f"<p>Errore: {str(e)}</p>"
        debug_html = f"<p>Debug: {str(e)}</p>"
    
    return result_html, debug_html
```

---

## 3. Esempi di Codice Completi

### 3.1 Esempio Base: Slider Semplice

```python
#!/usr/bin/env python3
"""Esempio base: Slider Gradio per filtro età minima."""

import gradio as gr
import pandas as pd
import numpy as np

# Dati di esempio
sample_data = {
    'Name': ['Player A', 'Player B', 'Player C', 'Player D'],
    'Age': [19, 25, 30, 22],
    'Position': ['FW', 'MF', 'DF', 'FW']
}
df_sample = pd.DataFrame(sample_data)

def filter_by_min_age(min_age):
    """Funzione callback per il filtro età."""
    filtered = df_sample[df_sample['Age'] >= min_age]
    summary = f"✅ Filtraggio: età >= {min_age} anni. Giocatori: {len(filtered)}"
    return filtered, summary

with gr.Blocks(title="Slider Età Base") as demo:
    gr.Markdown("## Esempio Base: Slider Filtro Età")
    
    with gr.Row():
        with gr.Column(scale=1):
            min_age_slider = gr.Slider(
                minimum=16, maximum=40, value=23, step=1,
                label="Età minima"
            )
            
        with gr.Column(scale=2):
            results_df = gr.Dataframe(label="Giocatori Filtrati")
            summary_md = gr.Markdown()
    
    # Connessione evento slider
    min_age_slider.change(
        fn=filter_by_min_age,
        inputs=min_age_slider,
        outputs=[results_df, summary_md]
    )

demo.launch()
```

### 3.2 Esempio Avanzato: Integrazione con Pipeline Esistente

```python
#!/usr/bin/env python3
"""Esempio avanzato: integrazione completa con la pipeline scout."""

import gradio as gr
import pandas as pd
import numpy as np
from scout_app import detect_columns, parse_value, normalize, age_factor

def process_with_min_age_filter(df, min_age_val, mode):
    """Processa i dati con filtro età minima.
    
    Args:
        df: DataFrame con dati giocatori
        min_age_val: int - Età minima
        mode: str - Modalità analisi
        
    Returns:
        tuple: (df_filtrato, html_riepilogo)
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(), "<p>Nessun dato disponibile</p>"
    
    df_processed = df.copy()
    
    # Rilevamento colonne e parsing
    cm = detect_columns(df_processed)
    df_processed['_price'] = df_processed[cm['Guide Value']].apply(parse_value)
    df_processed['_age'] = pd.to_numeric(df_processed[cm['Age']], errors='coerce')
    
    # Applica filtro età minima
    df_filtered = df_processed[df_processed['_age'] >= min_age_val].copy()
    
    riepilogo = f"""
    <div style='padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border-radius: 10px;'>
        <h3>🎯 Filtro Età Minima Attivo</h3>
        <p><strong>Età minima:</strong> {min_age_val} anni</p>
        <p><strong>Giocatori trovati:</strong> {len(df_filtered)}</p>
    </div>
    """
    
    return df_filtered, riepilogo

# Layout Gradio
with gr.Blocks(title="Scout App - Filtro Età Minima") as app:
    gr.Markdown("""
    # Football Scout Application
        
    ## Filtro Età Minima con Slider
        Usa lo slider per impostare l'età minima.
    """)
    
    with gr.Row():
        # Pannello controlli
        with gr.Column(scale=1):
            gr.Markdown("### Controlli Filtro")
            
            min_age_slider = gr.Slider(
                minimum=16, maximum=40, value=23, step=1,
                label="Età minima (anni)"
            )
            
            upload_btn = gr.Button("Carica CSV", variant="primary")
            clear_btn = gr.Button("Cancella Dati")
        
        # Pannello risultati
        with gr.Column(scale=2):
            data_input = gr.Dataframe(label="Dati Giocatori")
            results_df = gr.Dataframe(label="Risultati Filtrati")
            summary_md = gr.Markdown("### Riepilogo")
    
    # Event handlers
    def on_slider_change(age, df):
        """Callback per modifica slider."""
        if df is None or len(df) == 0:
            return pd.DataFrame(), "<p>Caricare prima un dataset.</p>"
        
        filtered_df, summary = process_with_min_age_filter(df, age, "winger")
        return filtered_df, summary
    
    def load_csv(file):
        """Carica file CSV."""
        if file is None:
            return pd.DataFrame(), "<p>Nessun file caricato.</p>"
        
        df = pd.read_csv(file)
        return df, f"✅ File caricato: {len(df)} righe"
    
    def clear_data():
        """Cancella tutti i dati."""
        return pd.DataFrame(), "<p>Dati cancellati.</p>"
    
    # Connessioni eventi
    min_age_slider.change(
        fn=on_slider_change,
        inputs=[min_age_slider, data_input],
        outputs=[results_df, summary_md]
    )
    upload_btn.click(fn=load_csv, inputs=upload_btn, outputs=[data_input, summary_md])
    clear_btn.click(fn=clear_data, outputs=[data_input, summary_md])

# Avvio applicazione
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
```

### 3.3 Esempio con Gestione Errori e Logging

```python
import logging
import gradio as gr
import pandas as pd

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def robust_age_filter(df, min_age):
    """Versione robusta con gestione errori completa."""
    try:
        if df is None or len(df) == 0:
            logger.warning("DataFrame vuoto ricevuto")
            return pd.DataFrame(), "<p>⚠️ Nessun dato nel DataFrame</p>"
        
        # Validazione tipo dati
        if not isinstance(df, pd.DataFrame):
            logger.error(f"Tipo non supportato: {type(df)}")
            return pd.DataFrame(), "<p>❌ Errore: input deve essere un DataFrame pandas</p>"
        
        # Controllo colonna età
        age_col = None
        for col in df.columns:
            if 'age' in col.lower():
                age_col = col
                break
        
        if age_col is None:
            logger.error("Colonna età non trovata")
            return pd.DataFrame(), "<p>❌ Colonna 'Age' non trovata nel DataFrame</p>"
        
        # Conversione sicura
        df_copy = df.copy()
        df_copy['_age_numeric'] = pd.to_numeric(df_copy[age_col], errors='coerce')
        
        # Filtro età minima
        valid_ages = df_copy['_age_numeric'].between(16, 45)
        filtered = df_copy[valid_ages & (df_copy['_age_numeric'] >= min_age)]
        
        logger.info(f"Filtro attivo: {len(filtered)} giocatori con età >= {min_age}")
        summary = f"✅ Filtro applicato: {len(filtered)} giocatori (età >= {min_age})"
        
        return filtered.drop(columns=['_age_numeric']), summary
        
    except Exception as e:
        logger.error(f"Errore nel processing: {e}", exc_info=True)
        return pd.DataFrame(), f"<p>❌ Errore: {str(e)}</p>"
```

---

## 4. Istruzioni per Test e Debug

### 4.1 Avvio dell'Applicazione

```bash
# Installazione dipendenze
pip install -r requirements.txt

# Avvio base
python guida_toggle_eta_gradio.md

# Avvio con configurazione custom
python guida_toggle_eta_gradio.md --server_name 0.0.0.0 --server_port 7860
```

### 4.2 Casi di Test da Verificare

Ecco i casi di test da verificare:

- **TC-01**: Slider a 23 → Solo giocatori >= 23 anni
- **TC-02**: Slider a 35 → Solo giocatori >= 35 anni
- **TC-03**: Slider a 18 (default) → Tutti i giocatori >= 18 anni
- **TC-04**: Slider modificato → Filtraggio aggiornato in tempo reale
- **TC-05**: DataFrame vuoto → Messaggio errore gestito
- **TC-06**: Valori età NaN → Gestiti correttamente (esclusi)

### 4.3 Debug Tips

```python
# Aggiungere logging per debug
import logging
logging.basicConfig(level=logging.DEBUG)

# Nel callback, aggiungere print temporanei:
print(f"[DEBUG] min_age={min_age}")
print(f"[DEBUG] DataFrame shape: {df.shape if df is not None else 'None'}")

# Per debug visivo, aggiungere un componente di output temporaneo:
debug_output = gr.Textbox(label="Debug Info")
```

### 4.4 Testing Manuale

```python
# Script di test rapido
import pandas as pd

def test_age_filter_logic():
    """Test della logica di filtro età minima."""
    
    # Dati di test
    test_df = pd.DataFrame({
        'Name': ['Player A', 'Player B', 'Player C', 'Player D'],
        'Age': [18, 25, 30, 22],
        'Guide Value': ['€5M', '€50M', '€10M', '€20M'],
        'Appearances': [30, 35, 28, 32]
    })
    
    # Test 1: min_age=23
    result_df, _ = process_with_min_age_filter(test_df, 23)
    assert len(result_df) == 2, "Dovrebbe filtrare a 2 giocatori (25, 30)"
    print("✅ Test 1 passato: min_age=23 filtra correttamente")
    
    # Test 2: min_age=20
    result_df, _ = process_with_min_age_filter(test_df, 20)
    assert len(result_df) == 3, "Dovrebbe filtrare a 3 giocatori (25, 30, 22)"
    print("✅ Test 2 passato: min_age=20 filtra correttamente")
    
    # Test 3: Range validazione
    try:
        process_with_min_age_filter(test_df, 10)  # Fuori range
        assert False, "Dovrebbe sollevare ValueError"
    except ValueError:
        print("✅ Test 3 passato: Validazione range età funziona")
    
    print("\n🎉 Tutti i test passati!")

# Esegui test
test_age_filter_logic()
```

### 4.5 Integrazione con Pipeline Esistente (app.py)

Per integrare lo slider nella pipeline esistente di `app.py`, modificare la funzione `process_analysis`:

```python
def process_analysis_with_min_age(df, mode, min_age, 
                                   min_price_val, price_val, min_apps, max_age):
    """Versione estesa che integra il filtro min_age nella pipeline esistente."""
    
    # ... (codice esistente di process_analysis) ...
    
    # Aggiungere dopo la rilevazione colonne:
    age_mask = (df_processed['_age'] >= min_age) & \
               (df_processed['_age'] < max_age) & \
               (df_processed['_age'].notna())
    
    # Applicare il mask ai filtri esistenti
    filtered_df = df_processed[
        (df_processed['_price'] >= min_price_euros) &
        (df_processed['_price'] <= max_price_euros) &
        (df_processed['_apps'] >= min_apps) &
        age_mask
    ].copy()
    
    # ... (resto della pipeline) ...
```

### 4.6 Pattern Gradio 2024-2025 Utilizzati

| Pattern | Descrizione | Vantaggio |
|---------|-------------|-----------|
| `gr.Slider` | Controllo continuo per range numerici | UX intuitiva e precisa |
| `gr.Row` / `gr.Column` con `scale` | Layout responsive | Adattivo a diverse risoluzioni |
| `.change()` event handler | Aggiornamento in tempo reale | Feedback immediato all'utente |
| Validazione input | Controllo tipi e range | Prevenzione errori runtime |
| Gestione eccezioni centralizzata | Try/except nel processing | Robustezza e logging |

### 4.7 Troubleshooting Comune

| Problema | Causa Probabile | Soluzione |
|----------|-----------------|-----------|
| Slider non si aggiorna | Evento `.change()` non connesso | Verificare la connessione eventi |
| Filtraggio non funziona | Colonna età non numerica | Usa `pd.to_numeric(errors='coerce')` |
| Nessun risultato dopo filtro | Valori NaN nella colonna età | Filtra con `.notna()` prima del confronto |
| Layout rotto | Scale non bilanciati | Usa `scale=1` e `scale=2` coerentemente |
| Errore TypeError | Mix di stringhe/numeri | Converti tutto con `errors='coerce'` |

---

## 5. Esempio Completo Funzionante (Eseguibile)

### 5.1 Codice Completo da Copiare e Usare

```python
#!/usr/bin/env python3
"""
Football Manager Scout Application - Slider Filtro Età Minima con Gradio

Questo esempio mostra come integrare uno slider Gradio per il filtro età minima
nella pipeline esistente di scout_app. Il componente include:
- gr.Slider per impostare l'età minima (range 16-45, default 18)
- Layout responsive con gr.Row e gr.Column
- Funzione di processing condizionale
- Gestione errori e validazione input

Eseguibile con: python guida_toggle_eta_gradio.md
"""

import gradio as gr
import pandas as pd
import numpy as np
from scout_app import detect_columns, parse_value, normalize, age_factor


# ============================================================================
# CONFIGURAZIONE E COSTANTI
# ============================================================================

# Range età supportati per i calciatori professionisti
AGE_MIN = 16
AGE_MAX = 45
DEFAULT_MIN_AGE = 18

# Percorso file CSV di esempio (relativo alla directory di lavoro)
SAMPLE_CSV_PATH = "sample_players.csv"


# ============================================================================
# FUNZIONI DI PROCESSING
# ============================================================================

def process_with_min_age_filter(
    df: pd.DataFrame,
    min_age: int,
    mode: str = "winger"
) -> tuple:
    """
    Processa i dati dei giocatori applicando il filtro età minima.
    
    Questa funzione integra il nuovo filtro min_age nella pipeline esistente,
    mantenendo la compatibilità con le modalità di analisi (winger, defensive_mid, coff).
    
    Args:
        df: DataFrame contenente i dati dei giocatori
        min_age: int - Età minima da applicare
        mode: str - Modalità analisi ("winger", "defensive_mid", "coff")
        
    Returns:
        tuple: (df_filtrato, html_riepilogo)
            - df_filtrato: DataFrame con i giocatori filtrati
            - html_riepilogo: Stringa HTML con informazioni sul filtraggio
            
    Raises:
        ValueError: Se la modalità non è valida o mancano colonne essenziali
        TypeError: Se i dati non sono di tipo appropriato
    """
    # Validazione input base
    if df is None or len(df) == 0:
        return pd.DataFrame(), "<p>⚠️ Nessun dato disponibile nel DataFrame</p>"
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Tipo non supportato: {type(df)}. Attendesi DataFrame pandas.")
    
    # Validazione modalità
    valid_modes = ["winger", "defensive_mid", "coff"]
    if mode not in valid_modes:
        raise ValueError(f"Modalità '{mode}' non valida. Scegli tra: {valid_modes}")
    
    # Validazione range età
    if not isinstance(min_age, (int, float)):
        raise TypeError(f"min_age deve essere un numero, ricevuto: {type(min_age)}")
    min_age = int(min_age)
    if min_age < AGE_MIN or min_age > AGE_MAX:
        raise ValueError(f"Età minima fuori range. Range valido: {AGE_MIN}-{AGE_MAX}")
    
    try:
        # Rilevamento colonne e preprocessing
        cm = detect_columns(df)
        df_processed = df.copy()
        
        # Conversione valori prezzo (gestisce formati come "€5.0M")
        df_processed['_price'] = df_processed[cm['Guide Value']].apply(parse_value)
        
        # Conversione età in numerico (gestisce valori non numerici con coerce)
        df_processed['_age'] = pd.to_numeric(df_processed[cm['Age']], errors='coerce')
        
        # Conversione presenze in numerico
        df_processed['_apps'] = pd.to_numeric(df_processed[cm['Appearances']], errors='coerce')
        
        # Conversione statistiche in numerico (per evitare TypeError nei confronti)
        all_stat_cols = [
            'Goal Contributions per 90', 'xG per 90', 'xA per 90', 'NP-xG per 90',
            'Shots on Target per 90', 'Key Passes per 90', 'Attacking Actions per 90',
            'Dribbling completati per 90', 'Passaggi progressivi per 90', 'Cross riusciti per 90',
            'xG Overperformance', 'Shots per 90',
            'Tackles per 90', 'Interceptions per 90', 'Progressive Passes per 90',
            'Pressures Attempted per 90', 'Possession Won per 90', 'Header Win %',
            'Pass Completion %', 'Average Rating'
        ]
        for col in all_stat_cols:
            if col in df_processed.columns:
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
        
        # Applica filtro età minima
        original_count = len(df_processed)
        df_filtered = df_processed[df_processed['_age'] >= min_age].copy()
        filtered_count = len(df_filtered)
        
        # Genera riepilogo HTML
        summary_html = f"""
        <div style='padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; border-radius: 10px;'>
            <h3 style='margin-top: 0;'>🎯 Filtro Età Minima Attivo</h3>
            <p><strong>Età minima selezionata:</strong> {min_age} anni</p>
            <p><strong>Giocatori originali:</strong> {original_count}</p>
            <p><strong>Giocatori dopo filtro:</strong> {filtered_count}</p>
            <p><strong>Riduzione:</strong> {((original_count - filtered_count) / original_count * 100):.1f}%</p>
        </div>
        """
        
        return df_filtered, summary_html
        
    except Exception as e:
        logger.error(f"Errore nel processing: {e}", exc_info=True)
        return pd.DataFrame(), f"<p>❌ Errore: {str(e)}</p>"


# ============================================================================
# FUNZIONI UI E EVENT HANDLERS
# ============================================================================

def load_sample_data() -> pd.DataFrame:
    """Carica i dati di esempio dal file CSV."""
    try:
        df = pd.read_csv(SAMPLE_CSV_PATH)
        return df
    except Exception as e:
        logger.error(f"Errore nel caricamento del campione: {e}")
        raise


def create_age_filter_ui():
    """Crea l'interfaccia Gradio per il filtro età minima."""
    
    with gr.Blocks(title="Football Scout - Filtro Età Minima") as app:
        gr.Markdown("""
        <h2>⚽ FM Scout - Filtro Età Minima</h2>
        <p>Usa lo slider per impostare l'età minima. 
           Verranno mostrati solo i giocatori con età >= valore selezionato.</p>
        """)
        
        with gr.Row():
            # Pannello controlli (sinistra)
            with gr.Column(scale=1):
                gr.Markdown("### Controlli Filtro")
                
                # Componente: Slider per età minima
                min_age_slider = gr.Slider(
                    minimum=AGE_MIN,
                    maximum=AGE_MAX,
                    value=DEFAULT_MIN_AGE,
                    step=1,
                    label="Età minima (anni)",
                    info=f"Range: {AGE_MIN}-{AGE_MAX} anni"
                )
                
                load_btn = gr.Button("Carica Campione", variant="primary")
                clear_btn = gr.Button("Cancella Dati")
            
            # Pannello risultati (destra)
            with gr.Column(scale=2):
                results_df = gr.Dataframe(label="Giocatori Filtrati")
                summary_md = gr.Markdown("### Riepilogo")
        
        # Event handlers
        def on_slider_change(min_age: int, df: pd.DataFrame) -> tuple:
            """
            Callback eseguito quando lo slider viene modificato.
            
            Args:
                min_age: Valore corrente dello slider
                df: DataFrame con i dati dei giocatori
                
            Returns:
                tuple: (df_filtrato, html_riepilogo)
            """
            if df is None or len(df) == 0:
                return pd.DataFrame(), "<p>⚠️ Caricare prima un dataset.</p>"
            
            # Chiamata alla funzione di processing con filtro condizionale
            filtered_df, summary = process_with_min_age_filter(df, min_age)
            return filtered_df, summary
        
        def load_sample() -> tuple:
            """Carica i dati di esempio dal file CSV."""
            try:
                df = load_sample_data()
                return df, f"✅ Campione caricato: {len(df)} giocatori"
            except Exception as e:
                error_msg = f"❌ Errore nel caricamento: {str(e)}"
                return pd.DataFrame(), error_msg
        
        def clear_data() -> tuple:
            """Cancella tutti i dati visualizzati."""
            return pd.DataFrame(), "<p>🗑️ Dati cancellati.</p>"
        
        # ========================================================================
        # CONNESSIONI EVENTI (Gradio 2024-2025 pattern)
        # ========================================================================
        
        # Quando lo slider viene modificato
        min_age_slider.change(
            fn=on_slider_change,
            inputs=[min_age_slider, results_df],
            outputs=[results_df, summary_md]
        )
        
        # Caricamento campione
        load_btn.click(fn=load_sample, outputs=[results_df, summary_md])
        
        # Cancella dati
        clear_btn.click(fn=clear_data, outputs=[results_df, summary_md])
    
    return app


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """
    Punto di ingresso principale per l'esecuzione dell'applicazione.
    
    Avvia il server Gradio sulla porta 7860 (localhost).
    """
    app = create_age_filter_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True,
        debug=True
    )


if __name__ == "__main__":
    main()
```

### 5.2 Istruzioni per l'Esecuzione

```bash
# Dalla directory del progetto, eseguire:
python guida_toggle_eta_gradio.md

# Oppure con Python direttamente:
python -m py_compile guida_toggle_eta_gradio.md  # Verifica sintassi
python guida_toggle_eta_gradio.md                # Esegui applicazione
```

### 5.3 Test di Validazione

```python
# Script di test rapido per validare il funzionamento
import pandas as pd

def test_age_filter_logic():
    """Test della logica di filtro età minima."""
    
    # Dati di test
    test_df = pd.DataFrame({
        'Name': ['Player A', 'Player B', 'Player C', 'Player D'],
        'Age': [18, 25, 30, 22],
        'Guide Value': ['€5M', '€50M', '€10M', '€20M'],
        'Appearances': [30, 35, 28, 32]
    })
    
    # Test 1: min_age=23
    result_df, _ = process_with_min_age_filter(test_df, 23)
    assert len(result_df) == 2, "Dovrebbe filtrare a 2 giocatori (25, 30)"
    print("✅ Test 1 passato: min_age=23 filtra correttamente")
    
    # Test 2: min_age=20
    result_df, _ = process_with_min_age_filter(test_df, 20)
    assert len(result_df) == 3, "Dovrebbe filtrare a 3 giocatori (25, 30, 22)"
    print("✅ Test 2 passato: min_age=20 filtra correttamente")
    
    # Test 3: Range validazione
    try:
        process_with_min_age_filter(test_df, 10)  # Fuori range
        assert False, "Dovrebbe sollevare ValueError"
    except ValueError:
        print("✅ Test 3 passato: Validazione range età funziona")
    
    print("\n🎉 Tutti i test passati!")

# Esegui test
test_age_filter_logic()
```

### 5.4 Integrazione con Pipeline Esistente (app.py)

Per integrare lo slider nella pipeline esistente di `app.py`, modificare la funzione `process_analysis`:

```python
def process_analysis_with_min_age(df, mode, min_age, 
                                   min_price_val, price_val, min_apps, max_age):
    """Versione estesa che integra il filtro min_age nella pipeline esistente."""
    
    # ... (codice esistente di process_analysis) ...
    
    # Aggiungere dopo la rilevazione colonne:
    age_mask = (df_processed['_age'] >= min_age) & \
               (df_processed['_age'] < max_age) & \
               (df_processed['_age'].notna())
    
    # Applicare il mask ai filtri esistenti
    filtered_df = df_processed[
        (df_processed['_price'] >= min_price_euros) &
        (df_processed['_price'] <= max_price_euros) &
        (df_processed['_apps'] >= min_apps) &
        age_mask
    ].copy()
    
    # ... (resto della pipeline) ...
```

### 5.5 Pattern Gradio 2024-2025 Utilizzati

| Pattern | Descrizione | Vantaggio |
|---------|-------------|-----------|
| `gr.Slider` | Controllo continuo per range numerici | UX intuitiva e precisa |
| `gr.Row` / `gr.Column` con `scale` | Layout responsive | Adattivo a diverse risoluzioni |
| `.change()` event handler | Aggiornamento in tempo reale | Feedback immediato all'utente |
| Validazione input | Controllo tipi e range | Prevenzione errori runtime |
| Gestione eccezioni centralizzata | Try/except nel processing | Robustezza e logging |

### 5.6 Troubleshooting Comune

| Problema | Causa Probabile | Soluzione |
|----------|-----------------|-----------|
| Slider non si aggiorna | Evento `.change()` non connesso | Verificare la connessione eventi |
| Filtraggio non funziona | Colonna età non numerica | Usa `pd.to_numeric(errors='coerce')` |
| Nessun risultato dopo filtro | Valori NaN nella colonna età | Filtra con `.notna()` prima del confronto |
| Layout rotto | Scale non bilanciati | Usa `scale=1` e `scale=2` coerentemente |
| Errore TypeError | Mix di stringhe/numeri | Converti tutto con `errors='coerce'` |

---

*Guida creata per Football Manager Scout Application - Integrazione Gradio + Slider Età Minima (Pattern 2024-2025)*