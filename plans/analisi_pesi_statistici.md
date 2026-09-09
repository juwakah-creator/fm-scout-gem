# Analisi Completa del Sistema di Pesi Statistico - FM Scout Gem

## 1. ELenco delle Metriche Offensive Attuali con i loro Pesi

### Metriche con Doppio Peso (2.0)
| Metrica | Simbolo | Peso | Ragione |
|---------|---------|------|---------|
| Goal Contributions per 90 | G+A/90 | **2.0** | Statistica predittiva chiave - somma gol e assist |
| xG per 90 | xG/90 | **2.0** | Metrica predittiva fondamentale - expected goals |
| xA per 90 | xA/90 | **2.0** | Metrica predittiva fondamentale - expected assists |

### Metriche con Peso Standard (1.0)
| Metrica | Simbolo | Peso | Ragione |
|---------|---------|------|---------|
| Shots on Target per 90 | SoT/90 | **1.0** | Tiri in porta realizzati |
| Key Passes per 90 | KP/90 | **1.0** | Passaggi decisivi che creano occasioni da gol |
| Attacking Actions per 90 | AA/90 | **1.0** | Somma di passaggi chiave, tiri e dribbling offensivi |
| NP-xG per 90 | NP-xG/90 | **1.0** | Expected Goals senza rigori - qualità dei gol reali |

### Metriche con Peso Ridotto (0.5)
| Metrica | Simbolo | Peso | Ragione |
|---------|---------|------|---------|
| xG Overperformance | xG OVP | **0.5** | Può essere rumore/stochasticità - differenza tra gol realizzati e xG atteso |

### Metriche Non Ponderate (ma calcolate)
| Metrica | Formula | Note |
|---------|---------|------|
| Shots per 90 | S/90 | Usata solo per calcolo efficienza offensiva |
| Appearances | Apps | Filtro minimo, non parte del punteggio |

---

## 2. ELenco delle Metriche Difensive Attuali con i loro Pesi

**Nota importante:** Il sistema attuale **NON include metriche difensive**. L'analisi è focalizzata esclusivamente sulle performance offensive.

Le uniche statistiche "difensive" presenti sono:
- **Appearances** (presenze) - usato come filtro minimo, non come metrica ponderata
- Nessun dato difensivo specifico (tackle, intercetti, ecc.)

---

## 3. Spiegazione di Come i Pesi Influenzano il Punteggio Finale

### Formula del Offensive Score
```python
Offensive Score = Σ(Metrica_i × Peso_i)
```

**Implementazione nel codice:**
```python
# Da winger.py, righe 116-135
if not pd.isna(goal_contributions_p90):
    offensive_score += goal_contributions_p90 * 2.0
if not pd.isna(xg_p90):  
    offensive_score += xg_p90 * 2.0
if not pd.isna(xa_p90):
    offensive_score += xa_p90 * 2.0

# Standard weights
if not pd.isna(shots_targeted_p90):
    offensive_score += shots_targeted_p90
if not pd.isna(key_passes_p90):
    offensive_score += key_passes_p90
if not pd.isna(attacking_actions_p90):
    offensive_score += attacking_actions_p90  
if not pd.isna(np_xg_p90):
    offensive_score += np_xg_p90

# Bonus per xG overperformance positiva
if not pd.isna(xg_overperformance) and xg_overperformance > 0:
    offensive_score += xg_overperformance * 2.0
```

### Formula del Value Index
```python
Value Index = (Offensive Score × Age Factor) / Guide Value
```

**Dove:**
- `Age Factor` varia da 1.0 a 2.0 in base all'età
- `Guide Value` è il prezzo di mercato del giocatore

### Normalizzazione Min-Max
Prima del calcolo finale, i punteggi vengono normalizzati:
```python
Normalized Value = (Value - Min) / (Max - Min)
```
Range risultato: [0, 1] dove 0 = minimo nel dataset, 1 = massimo.

---

## 4. Differenze tra Documentazione e Implementazione

### Differenza 1: Peso di xG Overperformance
| Aspetto | DOCUMENTAZIONE | IMPLEMENTAZIONE |
|---------|----------------|-----------------|
| **Peso** | 0.5 (sempre) | 2.0 (solo se > 0, bonus) |
| **Logica** | Peso ridotto standard | Bonus doppio per overperformance positiva |

**Codice documentazione:** `xG Overperformance → 0.5`
**Codice implementazione:** `xg_overperformance * 2.0` (se positivo)

### Differenza 2: Peso di NP-xG
| Aspetto | DOCUMENTAZIONE | IMPLEMENTAZIONE |
|---------|----------------|-----------------|
| **Peso** | 1.5 (medio-alto) | 1.0 (standard) |

**Codice documentazione:** `NP-xG per 90 → 1.5`
**Codice implementazione:** `np_xg_p90 * 1.0` (peso standard)

### Differenza 3: Normalizzazione
| Aspetto | DOCUMENTAZIONE | IMPLEMENTAZIONE |
|---------|----------------|-----------------|
| **Metodo** | Min-max su ogni metrica singolarmente | Min-max sul Offensive Score totale |

**Codice documentazione:** "Min-max su ogni metrica singolarmente"
**Codice implementazione:** `min_max_normalize(df_processed['Offensive Score'])` - normalizza il punteggio aggregato, non le singole metriche.

### Differenza 4: Colonne Richieste Minime
| Aspetto | DOCUMENTAZIONE | IMPLEMENTAZIONE |
|---------|----------------|-----------------|
| **Requisito** | Almeno 3 colonne offensive | Nessuna specifica |

**Codice documentazione:** "Almeno 3 offensive columns"
**Codice implementazione:** Nessun controllo esplicito, solo warning se mancano colonne.

### Differenza 5: Output
| Aspetto | DOCUMENTAZIONE | IMPLEMENTAZIONE |
|---------|----------------|-----------------|
| **Formato** | HTML con Bootstrap table | CSV + print a console |

---

## 5. Schema Riassuntivo dei Pesi Attuali

```
OFFENSIVE SCORE = 
    (G+A/90 × 2.0) +
    (xG/90 × 2.0) +
    (xA/90 × 2.0) +
    (SoT/90 × 1.0) +
    (KP/90 × 1.0) +
    (AA/90 × 1.0) +
    (NP-xG/90 × 1.0) +
    (xG OVP × 2.0 [solo se > 0])

VALUE INDEX = (Offensive Score × Age Factor) / Guide Value
```

**Distribuzione dei pesi:**
- Doppio peso (2.0): 3 metriche (37.5% del totale ponderato)
- Peso standard (1.0): 4 metriche (50% del totale ponderato)
- Bonus overperformance: 1 metrica (condizionale, 12.5%)

**Peso totale massimo teorico:** 10.0 (se tutte le metriche sono presenti e xG OVP > 0)