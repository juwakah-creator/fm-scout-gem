# Analisi Dettagliata per Goalkeeper.py

## 1. STRUTTURA DI WINGER.PY

### Funzioni Core Identificate:

#### a) `parse_guide_value(value)` (linee 27-55)
- **Scopo**: Parse del valore guida con formati €K/€M
- **Pattern comune**: Tutte le posizioni condividono questa funzione identica
- **Gestione errori**: Return NaN per valori invalidi, print warning

#### b) `calculate_age_factor(age)` (linee 58-79)
- **Scopo**: Moltiplicatore età per premiare giovani talenti
- **Scale**: 
  - age <= 20: 2.0x
  - 20 < age <= 23: 1.6x  
  - 24 <= age <= 26: 1.3x
  - age > 26: 1.0x

#### c) `calculate_offensive_score(row)` (linee 82-172)
- **Scopo**: Calcolo score composito con pesi specifici per posizione
- **Struttura**: 
  - Metriche offensive con pesi elevati (0.5-2.0x)
  - Metriche difensive con pesi moderati/bassi (0.1-0.4x)
  - Controllo NaN prima di ogni operazione
- **Pattern**: `if not pd.isna(metric): score += metric * weight`

#### d) `min_max_normalize(series)` (linee 175-191)
- **Scopo**: Normalizzazione min-max a range [0, 1]
- **Edge cases**: Series vuote o tutti valori uguali → return 0.0

#### e) `scale_value_index_to_100(series)` (linee 194-215)
- **Scopo**: Scaling Value Index da range raw a [0, 100]
- **Formula**: `(value - min) / (max - min) * 100`

#### f) `calculate_value_index(row, price_threshold)` (linee 218-260)
- **Scopo**: Value Index = (Offensive Score * Age Factor) / Price
- **Filtri**: 
  - Guide Value <= price_threshold (default 5M)
  - Age < max_age (default 30)
  - Min appearances (default 10)

#### g) `calculate_additional_metrics(row)` (linee 263-297)
- **Scopo**: Metriche aggiuntive per analisi avanzata
- **Output**: Dict con chiavi personalizzate per posizione

#### h) `process_football_data(input_file, output_file)` (linee 300-506)
- **Scopo**: Pipeline principale di elaborazione dati
- **Steps**:
  1. Read CSV
  2. Parse Guide Value
  3. Calculate scores
  4. Normalize scores
  5. Calculate value index
  6. Filter by criteria
  7. Sort and select top 20
  8. Save to CSV

#### i) `compute_dimension_scores(df)` (linee 509-669)
- **Scopo**: Calcolo punteggi dimensionali per stile di gioco
- **Dimensioni Winger**:
  - `finalizzazione_score`: Goal Contributions, xG, Shots on Target, xG Overperformance
  - `creazione_score`: xA, Key Passes, Passaggi progressivi
  - `pressing_score`: Pressures Attempted, Possession Won
  - `difesa_aerea_score`: Header Win %
  - `attacco_score`: Media delle 4 dimensioni

### Pattern di Gestione Errori:
- Try/except per FileNotFoundError, EmptyDataError, Exception generica
- Return None su errori critici
- Print warnings per problemi minori
- Controllo NaN prima di operazioni matematiche

---

## 2. INTEGRAZIONE IN APP.PY

### Struttura di Integrazione (linee 30-137):

#### a) `process_analysis(df, mode, ...)` (linee 30-137)
- **Routing**: Based on mode parameter
- **Valid modes**: ["winger", "defensive_mid", "strika", "defenders", "fullbacks", "coff"]
- **Filtri applicati**:
  - Price: min_price_val * 1M to max_price_val * 1M
  - Age: min_age to max_age
  - Appearances: >= min_apps

#### b) Funzioni di Processing per Posizione:
```python
if mode == "defensive_mid":
    result_html, debug_html = _process_defensive_mid(filtered_df, cm)
elif mode == "winger":
    result_html, debug_html = _process_winger(filtered_df, cm)
elif mode == "strika":
    result_html, debug_html = _process_striker(filtered_df, cm)
elif mode == "defenders":
    result_html, debug_html = _process_defender(filtered_df, cm)
elif mode == "fullbacks":
    result_html, debug_html = _process_fullback(filtered_df, cm)
elif mode == "coff":
    result_html, debug_html = _process_coff(filtered_df, cm)
```

#### c) Pattern Comune di Processing:
1. Calculate score per player (`df.apply(module.calculate_score, axis=1)`)
2. Normalize scores (`module.min_max_normalize()`)
3. Calculate value index (`module.calculate_value_index(row, price_threshold=int(1e18))`)
4. Scale to 0-100 (`module.scale_value_index_to_100()`)
5. Calculate additional metrics
6. Sort by Value Index, take top 20
7. Build result DataFrame with relevant columns
8. Generate HTML table

---

## 3. PATTERN COMUNI IN DEFENDERS.PY E STRIKA.PY

### Defenders.py (linee 1-100):
- **Struttura identica** a winger.py
- **Funzioni core**: `parse_guide_value`, `calculate_age_factor`
- **Score specifico**: `calculate_defender_score()` con pesi difensivi
- **Dimensioni**: Defensive actions, build-up play

### Strika.py (linee 1-100):
- **Struttura identica** a winger.py
- **Funzioni core**: `parse_guide_value`, `calculate_age_factor`
- **Score specifico**: `calculate_striker_score()` con pesi offensivi
- **Dimensioni**: Finalizzazione, creazione, pressing, difesa aerea

### Pattern Comuni:
1. **Import identici**: pandas, numpy, typing, os, sys
2. **Stessa struttura funzioni**: parse → calculate → normalize → value_index
3. **Stesso pattern error handling**: try/except con return None
4. **Dimension scores**: compute_dimension_scores() per tutte le posizioni

---

## 4. PROGETTAZIONE GOALKEEPER.PY

### Statistiche Specifiche per Portieri:

#### Metriche Offensive (per portieri):
- `Saves per 90`: Parate effettuate
- `Save Percentage %`: Percentuale parate
- `Clean Sheets %`: Percentuale partite senza gol subiti
- `Goals Conceded per 90`: Gol subiti

#### Metriche Difensive (per portieri):
- `Crosses Claimed %`: Cross intercettati
- `High Claims per 90`: Uscite alte
- `Sweeper Actions per 90`: Interventi fuori porta

#### Metriche Build-up:
- `Pass Completion %`: Percentuale passaggi
- `Progressive Passes per 90`: Passaggi progressivi
- `Distribution Accuracy %`: Precisione distribuzione

### Struttura Proposta:

```python
# Funzioni core (identiche alle altre posizioni)
def parse_guide_value(value): ...
def calculate_age_factor(age): ...

# Score specifico portiere
def calculate_goalkeeper_score(row):
    """
    Calcolo score composito per portieri.
    
    Pesi offensive (per portieri moderni):
    - Save Percentage % → 3.0x
    - Clean Sheets % → 2.5x
    - Goals Conceded per 90 → 2.0x (invertito: meno gol = meglio)
    
    Pesi build-up (portiere moderno):
    - Pass Completion % → 1.5x
    - Progressive Passes per 90 → 1.0x
    
    Pesi difensive tradizionali:
    - Saves per 90 → 1.5x
    - Crosses Claimed % → 1.0x
    """
    pass

def calculate_value_index(row, price_threshold=5000000): ...
def min_max_normalize(series): ...
def scale_value_index_to_100(series): ...

# Metriche aggiuntive specifiche
def calculate_additional_metrics(row):
    """Metriche per portieri:
    - Shot Stopping Efficiency
    - Distribution Quality
    - Claiming Ability
    """
    pass

# Dimension scores specifici
def compute_dimension_scores(df):
    """
    Dimensioni per portieri:
    - shot_stopping_score: Save Percentage, Goals Conceded
    - distribution_score: Pass Completion, Progressive Passes
    - claiming_score: Crosses Claimed, High Claims
    - modern_goalkeeper_score: Media delle 3 dimensioni
    """
    pass

def process_football_data(input_file='goalkeeper.csv', output_file='best_gk_prospects.csv'): ...
```

### Integrazione in app.py:

#### Modifiche richieste:
1. **Import**: `import goalkeeper`
2. **Valid modes**: Aggiungere `"goalkeeper"` alla lista
3. **Processing function**: `_process_goalkeeper(df, cm)`
4. **UI update**: Aggiungere opzione nel dropdown analisi

### Pattern da Seguire:
- Stessa struttura di winger.py/defenders.py/strika.py
- Funzioni con stessi nomi ma logica specifica per portieri
- Dimension scores personalizzati per ruolo portiere
- Error handling identico

---

## 5. STATISTICHE SPECIFICHE PER PORTIERI

### Da CSV (se presenti):
- `Saves per 90`
- `Save Percentage %`
- `Clean Sheets %`
- `Goals Conceded per 90`
- `Crosses Claimed %`
- `High Claims per 90`
- `Sweeper Actions per 90`
- `Pass Completion %`
- `Progressive Passes per 90`
- `Distribution Accuracy %`

### Se statistiche mancanti:
- Usare default values (50.0) come fatto in winger.py per difesa_aerea
- Gestire gracefully con NaN

---

## 6. PIANO IMPLEMENTAZIONE

### Fase 1: Creazione Goalkeeper.py
1. Copiare struttura da winger.py
2. Modificare `calculate_goalkeeper_score()` con pesi specifici
3. Aggiornare `compute_dimension_scores()` per portieri
4. Mantenere funzioni utility identiche

### Fase 2: Integrazione in app.py
1. Aggiungere import goalkeeper
2. Aggiungere "goalkeeper" a valid_modes
3. Creare `_process_goalkeeper(df, cm)` function
4. Aggiornare UI dropdown se necessario

### Fase 3: Testing
1. Test con sample_players.csv
2. Verifica calcolo punteggi
3. Verifica integrazione app.py
4. Test edge cases (NaN, valori mancanti)
