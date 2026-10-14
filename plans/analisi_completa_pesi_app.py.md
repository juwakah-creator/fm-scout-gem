# Analisi Completa dei Pesi Statistici in app.py e Moduli Archetipo

## 1. Riepilogo Architettura

`app.py` integra 7 moduli archetipo:
- `winger.py` → Attaccanti/ala
- `defensive_mid.py` → Centrocampisti difensivi
- `strika.py` → Attaccanti (finitura)
- `defenders.py` → Difensori
- `fullbacks.py` → Terzini
- `cof.py` → Mediani offensivi creativi
- `goalkeeper.py` → Portieri

---

## 2. Pesi per Archetipo - Confronto Modulo vs app.py

### 2.1 WINGER (winger.py)

**Pesi implementati in `calculate_offensive_score`:**

| Metrica | Peso | Note |
|---------|------|------|
| Goal Contributions per 90 | **2.0** | Predittivo chiave |
| xG per 90 | **2.0** | Expected goals |
| xA per 90 | **2.0** | Expected assists |
| NP-xG per 90 | **1.5** | Aggiornato da 1.0 a 1.5 |
| Dribbling completati per 90 | **1.2** | Nuova metrica |
| Shots on Target per 90 | **1.0** | Standard |
| Key Passes per 90 | **1.0** | Standard |
| Attacking Actions per 90 | **1.0** | Standard |
| Passaggi progressivi per 90 | **1.0** | Nuova metrica |
| Cross riusciti per 90 | **1.0** | Nuova metrica |
| xG Overperformance | **0.5** | Ridotto da 2.0 a 0.5 |
| Pressures Attempted per 90 | **0.4** | Metrica difensiva bassa |
| Possession Won per 90 | **0.3** | Metrica difensiva bassa |
| Pressing Efficiency | **0.2** | Metrica difensiva bassa |
| Header Win % | **0.1** | Metrica difensiva bassa |

**Integrazione in app.py:** ✅ Corretta - usa `winger.calculate_offensive_score` e `winger.scale_value_index_to_100`

---

### 2.2 DEFENSIVE MID (defensive_mid.py)

**Pesi implementati in `calculate_defensive_score`:**

| Metrica | Peso | Categoria |
|---------|------|-----------|
| Tackles per 90 | **2.0** | Alto impatto |
| Interceptions per 90 | **1.6** | Alto impatto |
| Pass Completion % | **1.6** | Alto impatto |
| Progressive Passes per 90 | **1.3** | Alto impatto |
| Pressures Attempted per 90 | **1.3** | Alto impatto |
| Possession Won per 90 | **1.1** | Alto impatto |
| Header Win % | **1.1** | Alto impatto |
| Average Rating | **0.9** | Moderato |
| Key Passes per 90 | **0.7** | Moderato |
| Shots Blocked per 90 | **0.4** | Moderato |
| xG Overperformance | **0.4** | Moderato (solo se > 0) |
| Goal Contributions per 90 | **0.3** | Moderato |
| Mistakes Leading to Goals | **-0.7** | Negativo (penalità) |

**Integrazione in app.py:** ✅ Corretta - usa `defensive_mid.calculate_defensive_score` e `defensive_mid.scale_value_index_to_100`

---

### 2.3 STRIKA (strika.py)

**Pesi implementati in `calculate_striker_score`:**

| Metrica | Peso | Note |
|---------|------|------|
| Goal Contributions per 90 | **2.0** | Predittivo chiave |
| xG_Adjusted | **2.0** | Formula: (NP-xG * 1.7) + (xG * 0.3), poi * 2.0 |
| Key Passes per 90 | **1.5** | Creazione |
| xA per 90 | **1.5** | Assist attesi |
| Shots on Target per 90 | **1.2** | Tiri in porta |
| Shots per 90 | **1.0** | Volume tiri |
| Pressures Attempted per 90 | **0.8** | Pressing |
| Pass Completion % | **0.5** | Precisione |

**Formula speciale xG_Adjusted:**
```python
xg_adjusted = (np_xg_p90 * 1.7) + (xg_p90 * 0.3)
striker_score += xg_adjusted * 2.0
```

**Integrazione in app.py:** ✅ Corretta - usa `strika.calculate_striker_score` e `strika.scale_value_index_to_100`

---

### 2.4 DEFENDERS (defenders.py)

**Pesi implementati in `calculate_defender_score`:**

| Metrica | Peso | Categoria |
|---------|------|-----------|
| Defensive Actions per 90 | **3.0** | Difesa alta |
| Tackles per 90 | **2.5** | Difesa alta |
| Interceptions per 90 | **2.5** | Difesa alta |
| Possession Won per 90 | **2.0** | Difesa alta |
| Clearances per 90 | **1.5** | Difesa media |
| Blocks per 90 | **1.5** | Difesa media |
| Pressures Attempted per 90 | **1.0** | Difesa media |
| Progressive Passes per 90 | **2.5** | Build-up |
| Key Passes per 90 | **2.0** | Build-up |
| Creative Actions per 90 | **2.0** | Build-up |
| Pass Completion % | **1.5** | Build-up |
| Progressive Pass % | **1.5** | Build-up |
| Passes Completed per 90 | **1.0** | Build-up |
| Goal Contributions per 90 | **2.0** | Altro |
| Average Rating | **1.5** | Altro |
| Header Win % | **1.5** | Altro |
| Dribbles per 90 | **0.5** | Altro |

**Integrazione in app.py:** ✅ Corretta - usa `defenders.calculate_defender_score` e `defenders.scale_value_index_to_100`

---

### 2.5 FULLBACKS (fullbacks.py)

**Pesi implementati in `calculate_fullback_score`:**

| Metrica | Peso | Categoria |
|---------|------|-----------|
| Defensive Actions per 90 | **2.5** | Difesa |
| Possession Won per 90 | **2.0** | Difesa |
| Blocks per 90 | **1.8** | Difesa |
| Pressures Attempted per 90 | **1.5** | Difesa |
| xA per 90 | **2.5** | Creativo |
| Key Passes per 90 | **3.0** | Creativo (max!) |
| Progressive Passes per 90 | **2.0** | Creativo |
| Progressive Pass % | **2.5** | Creativo |
| Open Play Cross Completion % | **1.8** | Creativo |
| Clear Cut Chances Created | **2.0** | Creativo |
| Crosses Completed | **2.5** | Creativo |
| Dribbles per 90 | **1.5** | Attacco |
| Goal Contributions per 90 | **1.5** | Attacco |
| xG per 90 | **1.0** | Attacco |
| xG Overperformance | **0.5** | Attacco |
| Header Win % | **1.5** | Attacco |
| Mistakes Leading to Goals | **-2.0** | Negativo (penalità) |

**Integrazione in app.py:** ✅ Corretta - usa `fullbacks.calculate_fullback_score` e `fullbacks.scale_value_index_to_100`

---

### 2.6 COF (cof.py)

**Pesi implementati in `calculate_cof_score`:**

| Metrica | Peso | Categoria |
|---------|------|-----------|
| xA per 90 | **2.0** | Creativo alto |
| Key Passes per 90 | **1.8** | Creativo alto |
| Goal Contributions per 90 | **1.6** | Creativo alto |
| Passaggi progressivi per 90 | **1.3** | Creativo medio |
| xG per 90 | **1.5** | Finitura medio-alto |
| NP-xG per 90 | **1.2** | Finitura medio-alto |
| Shots on Target per 90 | **1.0** | Finitura standard |
| Dribbling completati per 90 | **1.0** | Finitura standard |
| xG Overperformance | **0.5** | Finitura (solo se > 0) |
| Pressures Attempted per 90 | **0.4** | Difensivo basso |
| Possession Won per 90 | **0.3** | Difensivo basso |
| Header Win % | **0.1** | Difensivo basso |

**Integrazione in app.py:** ✅ Corretta - usa `cof.calculate_cof_score` e `cof.scale_value_index_to_100`

---

### 2.7 GOALKEEPER (goalkeeper.py)

**Pesi implementati in `calculate_goalkeeper_score`:**

| Metrica | Peso | Categoria |
|---------|------|-----------|
| Save Percentage % | **3.0** | Shot-stopping alto |
| Clean Sheets % | **2.5** | Shot-stopping alto |
| Goals Conceded per 90 | **2.0** (inverted) | Shot-stopping alto - formula: `(10 - goals_conceded_p90) * 2.0` |
| Saves per 90 | **1.5** | Shot-stopping medio |
| Pass Completion % | **1.5** | Distribution medio |
| Progressive Passes per 90 | **1.0** | Distribution medio |
| Distribution Accuracy % | **1.0** | Distribution medio |
| Crosses Claimed % | **1.0** | Claiming basso |
| High Claims per 90 | **0.8** | Claiming basso |
| Sweeper Actions per 90 | **0.5** | Claiming basso |

**Formula speciale Goals Conceded:**
```python
goalkeeper_score += (10 - goals_conceded_p90) * 2.0
```
Questa formula inverte la metrica: meno gol subiti = punteggio più alto.

**Integrazione in app.py:** ✅ Corretta - usa `goalkeeper.calculate_goalkeeper_score` e `goalkeeper.scale_value_index_to_100`

---

## 3. DISCREPANZE TROVATE

### 🔴 CRITICHE

#### 3.1 Funzione Legacy `run_scout_analysis` con Pesi Hardcoded in app.py (Righe 1260-1285)

**Problema:** La funzione legacy contiene pesi hardcoded che **NON corrispondono** a quelli del modulo `winger.py`:

```python
# app.py righe 1260-1269 - PESI LEGACY HARDCODED:
weights = {
    'Goal Contributions per 90': 2.0,   # ✅ Corretto (uguale a winger)
    'xG per 90': 2.0,                    # ✅ Corretto (uguale a winger)
    'xA per 90': 2.0,                    # ✅ Corretto (uguale a winger)
    'Shots on Target per 90': 1.0,       # ✅ Corretto (uguale a winger)
    'Key Passes per 90': 1.0,            # ✅ Corretto (uguale a winger)
    'Attacking Actions per 90': 1.0,     # ✅ Corretto (uguale a winger)
    'NP-xG per 90': 1.5,                 # ✅ Corretto (uguale a winger)
    'xG Overperformance': 0.5            # ✅ Corretto (uguale a winger)
}
```

**Verdetto:** I pesi legacy sono **coincidenti** con quelli di winger.py. Tuttavia, la funzione legacy:
- Usa `normalize()` da scout_app invece di `min_max_normalize()` da winger.py
- Calcola l'Offensive Score come media ponderata (`offensive_score / weight_sum`) invece di somma semplice
- Questo crea **differenze numeriche** nei risultati se chiamata

#### 3.2 Differenza nel Calcolo dell'Age Factor

| Modulo | Formula Age Factor |
|--------|-------------------|
| `scout_app.age_factor()` | Non visibile (importato) |
| `winger.calculate_age_factor()` | ≤20: 2.0, 21-23: 1.6, 24-26: 1.3, >26: 1.0 |
| `defensive_mid.calculate_age_factor()` | ≤20: 2.0, 21-23: 1.6, 24-26: 1.3, >26: 1.0 |
| `strika.calculate_age_factor()` | ≤20: 2.0, 21-23: 1.6, 24-26: 1.3, >26: 1.0 |
| `defenders.calculate_age_factor()` | ≤20: 2.0, 21-23: 1.6, 24-26: 1.3, >26: 1.0 |
| `cof.calculate_age_factor()` | ≤20: 2.0, 21-23: 1.6, 24-26: 1.3, >26: 1.0 |
| `goalkeeper.calculate_age_factor()` | ≤20: 2.0, 21-23: 1.6, 24-26: 1.3, >26: 1.0 |
| `fullbacks.calculate_value_index()` | **DIVERSO**: ≤23: 1.2, 24-27: 1.0, 28-30: 0.8, >30: 0.6 |

**Problema:** `fullbacks.py` usa una formula dell'age factor **diversa** dagli altri moduli! Questo crea un'**incoerenza sistematica** nei fullback.

#### 3.3 Differenza nel Calcolo del Value Index

| Modulo | Formula Value Index |
|--------|---------------------|
| `winger`, `defensive_mid`, `strika`, `defenders`, `cof`, `goalkeeper` | `(score * age_factor) / price` |
| `fullbacks.calculate_value_index()` | `(score * age_factor) / price` (stessa formula, ma age_factor diverso) |

**Verdetto:** La formula è la stessa, ma l'age_factor diverso in fullbacks crea risultati non comparabili.

---

### 🟡 MODERATE

#### 3.4 Normalizzazione Min-Max Diverse

Alcuni moduli usano `min_max_normalize()` con comportamento leggermente diverso:

| Modulo | Comportamento edge case (tutti uguali) |
|--------|---------------------------------------|
| `winger.min_max_normalize()` | Restituisce `[0.0] * len` se min == max |
| `defensive_mid.min_max_normalize()` | Restituisce `[0.0] * len` se min == max |
| `strika.min_max_normalize()` | Restituisce `[0.0] * len` se min == max |
| `defenders.min_max_normalize()` | Restituisce `[0.0] * len` se min == max |
| `cof.min_max_normalize()` | Restituisce `[0.0] * len` se min == max |
| `goalkeeper.min_max_normalize()` | Restituisce `[0.0] * len` se min == max |
| `fullbacks.min_max_normalize()` | **DIVERSO**: Restituisce `[0.5] * len` se min == max |

**Problema:** I fullback normalizzano a 0.5 quando tutti i valori sono uguali, mentre gli altri moduli normalizzano a 0.0. Questo crea un'**incoerenza di ±50 punti** nello scale_value_index_to_100.

#### 3.5 Differenza nel Trattamento di xG Overperformance

| Modulo | Peso xG Overperformance | Condizione |
|--------|------------------------|------------|
| `winger` | **0.5** | Sempre (senza condizione) |
| `cof` | **0.5** | Solo se > 0 |
| `defensive_mid` | **0.4** | Solo se > 0 |
| `strika` | Non presente direttamente | Usata in xG_Adjusted |

**Nota:** In `winger.py` la riga 159-160 applica il peso solo se `xg_overperformance > 0`, quindi è coerente con cof e defensive_mid.

---

### 🟢 MINORI / NOTE

#### 3.6 Metriche Non Presenti in Alcuni Moduli

| Metrica | winger | DM | Strika | Defenders | Fullbacks | COF | GK |
|---------|--------|----|--------|-----------|-----------|------|-----|
| Mistakes Leading to Goals | ❌ | ✅ (-0.7) | ❌ | ❌ | ✅ (-2.0) | ❌ | ❌ |
| Creative Actions per 90 | ❌ | ❌ | ❌ | ✅ (2.0) | ❌ | ❌ | ❌ |
| Clearances per 90 | ❌ | ❌ | ❌ | ✅ (1.5) | ❌ | ❌ | ❌ |
| Save Percentage % | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (3.0) |
| Clean Sheets % | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (2.5) |

**Verdetto:** Le metriche specifiche per ruolo sono corrette e non creano conflitti.

#### 3.7 Differenza nel Nome della Colonna "Defender Score"

In `fullbacks.py` riga 145:
```python
if "Defender Score" in row.index:
    score = row["Defender Score"]
elif "Fullback Score" in row.index:
    score = row["Fullback Score"]
```

**Problema:** Il fullback cerca prima `"Defender Score"` invece di `"Fullback Score"`. Questo è un refactoring incompleto o un errore di naming. Dovrebbe cercare `"Fullback Score"` per primo.

---

## 4. RIASSUNTO DISCREPANZE

| # | Problema | Gravità | Moduli Interessati |
|---|----------|---------|-------------------|
| 1 | Age Factor diverso in fullbacks.py | 🔴 Alta | fullbacks vs tutti gli altri |
| 2 | Normalizzazione diversa in fullbacks.min_max_normalize() | 🟡 Media | fullbacks vs tutti gli altri |
| 3 | Ricerca "Defender Score" invece di "Fullback Score" | 🟡 Media | fullbacks.py |
| 4 | Funzione legacy run_scout_analysis con logica diversa | 🟢 Bassa | app.py (solo se chiamata) |
| 5 | xG Overperformance peso variabile tra moduli | 🟢 Bassa | winger/cof/defensive_mid |

---

## 5. RACCOMANDAZIONI

### Priorità Alta
1. **Uniformare l'Age Factor** in fullbacks.py per usare la stessa formula degli altri moduli (≤20: 2.0, 21-23: 1.6, 24-26: 1.3, >26: 1.0)
2. **Uniformare la normalizzazione** in fullbacks.min_max_normalize() per restituire [0.0] quando min == max

### Priorità Media
3. **Correggere il naming** in fullbacks.calculate_value_index(): cercare "Fullback Score" prima di "Defender Score"
4. **Deprecare run_scout_analysis()** o uniformarla al nuovo sistema per evitare risultati inconsistenti

### Priorità Bassa
5. **Documentare** le differenze di peso xG Overperformance tra moduli (0.4 vs 0.5) e standardizzare

---

## 6. CONCLUSIONE

L'integrazione tra `app.py` e i moduli archetipo è **sostanzialmente corretta**. I pesi statistici sono ben bilanciati e proporzionati ai vari ruoli. Le uniche anomalie significative riguardano il modulo `fullbacks.py` che presenta:
- Formula age_factor diversa
- Comportamento normalizzazione diverso
- Possible errore di naming

Tutti gli altri moduli (winger, defensive_mid, strika, defenders, cof, goalkeeper) sono **coerenti e ben integrati** in app.py.
