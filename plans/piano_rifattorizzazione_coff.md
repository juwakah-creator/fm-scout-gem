# Piano di Rifattorizzazione Sistema COF

## Obiettivi
1. Eliminare colonna "COFF Score" dalla tabella → sostituire con "Index Value" (max 100, dinamico)
2. Eliminare completamente "COFF Profile Generator"
3. Rendere visibili le statistiche avanzate usate per calcolare l'index

## Analisi Struttura Attuale

### File Principali
- `app.py` (845 righe): UI Gradio + logica di processo
- `cof.py` (810 righe): Calcolo punteggi COF + PlayerProfileGenerator
- `scout_app.py` (476 righe): Utility functions (normalize, age_factor, detect_columns)
- `winger.py`, `defensive_mid.py`: Moduli di riferimento per pattern da seguire

### Dipendenze Identificate
```
app.py
├── process_analysis() → _process_cof()
│   └── cof.PlayerProfileGenerator (da eliminare)
├── create_ui()
│   └── Checkbox "COF Profile Generator" (da eliminare)
└── import cof

cof.py
├── calculate_cof_score() → da mantenere
├── min_max_normalize() → da mantenere
├── scale_value_index_to_100() → da mantenere
├── calculate_value_index() → da adattare
├── compute_dimension_scores() → da usare per stats avanzate
└── PlayerProfileGenerator (classe da eliminare)
```

## Piano di Implementazione

### Fase 1: Modifiche a `cof.py`

#### 1.1 Rimuovere PlayerProfileGenerator
- Eliminare classe completa (righe 641-769)
- Rimuovere import json se non usato altrove

#### 1.2 Adattare calculate_value_index()
```python
# Vecchio: usa COF Score come input
value_index = (cof_score * age_factor) / parsed_price

# Nuovo: calcola direttamente dalle statistiche pesate
def calculate_value_index(row, price_threshold=5000000):
    guide_value = row.get('Guide Value', np.nan)
    age = pd.to_numeric(row.get('Age', np.nan), errors='coerce')
    
    # Calcola score direttamente dalle statistiche
    cof_score = calculate_cof_score(row)
    age_factor = calculate_age_factor(age)
    
    if pd.isna(guide_value) or pd.isna(age) or pd.isna(cof_score):
        return np.nan
    
    parsed_price = parse_guide_value(guide_value)
    if pd.isna(parsed_price) or parsed_price > price_threshold:
        return np.nan
    if parsed_price <= 0:
        return np.nan
    
    return (cof_score * age_factor) / parsed_price
```

#### 1.3 Mantenere compute_dimension_scores()
- Questa funzione calcola già i 5 dimension scores
- Sarà usata per rendere visibili le statistiche avanzate

### Fase 2: Modifiche a `app.py`

#### 2.1 Riscrivere _process_cof()
```python
def _process_cof(df, cm):
    """Process COF analysis using weighted statistics and Index Value."""
    try:
        # Calculate COF score (weighted stats)
        df['COF Score'] = df.apply(cof.calculate_cof_score, axis=1)
        
        # Normalize scores
        df['Normalized COF Score'] = cof.min_max_normalize(df['COF Score'])
        
        # Calculate Value Index and scale to 0-100
        df['Value Index'] = df.apply(
            lambda row: cof.calculate_value_index(row, price_threshold=int(1e18)),
            axis=1
        )
        df['Value Index'] = cof.scale_value_index_to_100(df['Value Index'])
        
        # Calculate dimension scores for advanced stats visibility
        dim_scores = cof.compute_dimension_scores(df)
        for col in ['finalizzazione_score', 'creazione_score', 'dribbling_score',
                    'pressing_score', 'attacco_score']:
            if col in dim_scores.columns:
                df[col] = dim_scores[col]
        
        # Age factor
        df['Age Factor'] = df['_age'].apply(age_factor)
        
        # Sort and take top 20
        sorted_results = df.sort_values('Value Index', ascending=False, na_position='last').head(20)
        
        # Build result DataFrame with advanced stats visible
        result_df = pd.DataFrame()
        result_df['Name'] = sorted_results['Name']
        result_df['Club'] = sorted_results['Club']
        result_df['Age'] = sorted_results['_age'].round(1)
        result_df['Guide Value'] = sorted_results[cm['Guide Value']]
        result_df['Value Index'] = sorted_results['Value Index'].round(2)  # Max 100
        result_df['COF Score'] = sorted_results['COF Score'].round(2)
        result_df['Age Factor'] = sorted_results['Age Factor'].round(2)
        
        # Add advanced stats columns
        advanced_stats = [
            'xA per 90', 'Key Passes per 90', 'Goal Contributions per 90',
            'Passaggi progressivi per 90', 'xG per 90', 'NP-xG per 90',
            'Shots on Target per 90', 'Dribbling completati per 90',
            'Pressures Attempted per 90', 'Possession Won per 90', 'Header Win %'
        ]
        
        for stat in advanced_stats:
            if stat in sorted_results.columns:
                result_df[stat] = sorted_results[stat].round(2)
        
        # Add dimension scores
        dim_cols = ['finalizzazione_score', 'creazione_score', 'dribbling_score', 
                    'pressing_score', 'attacco_score']
        for col in dim_cols:
            if col in sorted_results.columns:
                result_df[col] = sorted_results[col].round(1)
        
        # Generate HTML table...
```

#### 2.2 Rimuovere UI element COF Profile Generator
- Eliminare checkbox `cof_toggle` da `create_ui()` (righe 770-774)
- Aggiornare docstring e commenti

### Fase 3: Testing

#### Test da eseguire:
1. Verificare che Index Value sia scalato 0-100
2. Confermare scomparsa colonna COF Score dalla tabella finale
3. Verificare visibilità statistiche avanzate (dimension scores)
4. Testare integrazione con altri mode (winger, defensive_mid)
5. Eseguire test esistenti per regressione

## File da Modificare
1. `cof.py` - Rimuovere PlayerProfileGenerator, adattare calculate_value_index
2. `app.py` - Riscrivere _process_cof(), rimuovere UI element

## Note Tecniche
- Il pattern da seguire è quello di `winger.py`/`defensive_mid.py` dove Value Index è già scalato 0-100
- Le statistiche avanzate devono essere calcolate con `compute_dimension_scores()` e incluse nella tabella
- Mantenere backward compatibility per i test esistenti
