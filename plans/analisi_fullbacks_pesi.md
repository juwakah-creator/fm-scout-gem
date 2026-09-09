# Analisi Sistematica dei Pesi Statistici - Fullbacks

## 1. Riepilogo dei Pesi Attuali

### FULLBACK_WEIGHTS (righe 14-32)
```python
FULLBACK_WEIGHTS = {
    "Defensive Actions per 90": 2.5,
    "Possession Won per 90": 2.0,
    "Blocks per 90": 1.8,
    "Pressures Attempted per 90": 1.5,
    "xA per 90": 2.5,
    "Key Passes per 90": 3.0,
    "Progressive Passes per 90": 2.0,
    "Progressive Pass %": 2.5,
    "Open Play Cross Completion %": 1.8,
    "Clear Cut Chances Created": 2.0,
    "Crosses Completed": 2.5,
    "Dribbles per 90": 1.5,
    "Goal Contributions per 90": 1.5,
    "xG per 90": 1.0,
    "xG Overperformance": 0.5,
    "Header Win %": 1.5,
    "Mistakes Leading to Goals": -2.0
}
```

### Pesi in calculate_fullback_score (righe 47-106)
La funzione usa pesi **locali** che differiscono parzialmente da FULLBACK_WEIGHTS:

| Categoria | Metrica | Peso Funzione | Peso DIZIONARIO | Differenza |
|-----------|---------|---------------|-----------------|------------|
| Difesa | Defensive Actions per 90 | 2.5 | 2.5 | ✓ Uguale |
| Difesa | Possession Won per 90 | 2.0 | 2.0 | ✓ Uguale |
| Difesa | Blocks per 90 | 1.8 | 1.8 | ✓ Uguale |
| Difesa | Pressures Attempted per 90 | 1.5 | 1.5 | ✓ Uguale |
| Creatività | xA per 90 | 2.5 | 2.5 | ✓ Uguale |
| Creatività | Key Passes per 90 | 3.0 | 3.0 | ✓ Uguale |
| Creatività | Progressive Passes per 90 | 2.0 | 2.0 | ✓ Uguale |
| Creatività | Progressive Pass % | 2.5 | 2.5 | ✓ Uguale |
| Creatività | Open Play Cross Completion % | 1.8 | 1.8 | ✓ Uguale |
| Creatività | Clear Cut Chances Created | 2.0 | 2.0 | ✓ Uguale |
| Creatività | Crosses Completed | 2.5 | 2.5 | ✓ Uguale |
| Attacco | Dribbles per 90 | 1.5 | 1.5 | ✓ Uguale |
| Attacco | Goal Contributions per 90 | 1.5 | 1.5 | ✓ Uguale |
| Attacco | xG per 90 | 1.0 | 1.0 | ✓ Uguale |
| Attacco | xG Overperformance | 0.5 | 0.5 | ✓ Uguale |
| Attacco | Header Win % | 1.5 | 1.5 | ✓ Uguale |
| Negativa | Mistakes Leading to Goals | -2.0 | -2.0 | ✓ Uguale |

**Nota:** I pesi sono coerenti tra dizionario e funzione, ma la funzione non usa il dizionario per tutte le metriche (usa dictionary locali).

---

## 2. Analisi dei Pesi per Categoria

### 2.1 Metriche Difensive (Peso Totale: 7.8)
| Metrica | Peso | Valutazione FM | Note |
|---------|------|----------------|------|
| Defensive Actions per 90 | **2.5** | ✅ Alto | Corretto - fondamentale per terzino difensivo |
| Possession Won per 90 | **2.0** | ✅ Medio-Alto | Appropriato per pressing e recupero |
| Blocks per 90 | **1.8** | ✅ Medio | Utile ma non primario per terzino |
| Pressures Attempted per 90 | **1.5** | ✅ Medio | Corretto - pressione è importante |

**Totale Difesa: 7.8** (24% del peso totale)

### 2.2 Metriche Creative/Costruttive (Peso Totale: 16.3)
| Metrica | Peso | Valutazione FM | Note |
|---------|------|----------------|------|
| xA per 90 | **2.5** | ✅ Alto | Corretto - assist attesi sono cruciali |
| Key Passes per 90 | **3.0** | ⚠️ **Elevato** | Il peso più alto - forse eccessivo? |
| Progressive Passes per 90 | **2.0** | ✅ Medio-Alto | Appropriato |
| Progressive Pass % | **2.5** | ✅ Alto | Corretto - precisione passaggi |
| Open Play Cross Completion % | **1.8** | ✅ Medio | Utile ma non primario |
| Clear Cut Chances Created | **2.0** | ✅ Medio-Alto | Appropriato |
| Crosses Completed | **2.5** | ✅ Alto | Corretto - crossing è ruolo chiave |

**Totale Creatività: 16.3** (51% del peso totale)

### 2.3 Metriche Offensive/Attaccanti (Peso Totale: 6.0)
| Metrica | Peso | Valutazione FM | Note |
|---------|------|----------------|------|
| Dribbles per 90 | **1.5** | ✅ Medio | Appropriato per terzino moderno |
| Goal Contributions per 90 | **1.5** | ✅ Medio | Corretto - gol+assist |
| xG per 90 | **1.0** | ✅ Basso | Appropriato - terzini non sono finalisti |
| xG Overperformance | **0.5** | ✅ Molto Basso | Corretto - rumore statistico |
| Header Win % | **1.5** | ✅ Medio | Utile per duel aerei |

**Totale Attacco: 6.0** (19% del peso totale)

### 2.4 Metrica Negativa
| Metrica | Peso | Valutazione FM | Note |
|---------|------|----------------|------|
| Mistakes Leading to Goals | **-2.0** | ✅ Alto (penalità) | Corretto - errori costano molto |

---

## 3. Analisi della Distribuzione dei Pesi

### Ripartizione Percentuale
```
DIFESA:      7.8   (24%)  ████████░░░░░░░░░░░░
CREATIVITÀ: 16.3   (51%)  ████████████████████
ATTACCO:    6.0   (19%)  ██████░░░░░░░░░░░░░░
NEGATIVA:   2.0   (6%)   ██░░░░░░░░░░░░░░░░░░
```

**Totale Pesi Positivi: 31.8**
**Peso Metrica Negativa: 2.0**

---

## 4. Confronto con Best Practice FM per Terzini

### Ruolo del Terzino in Football Manager
Un terzino moderno deve eccellere in:
1. **Difesa** (40-50% importanza) - tackling, intercetti, clearing
2. **Crossing/Assist** (30-40% importanza) - cross, passaggi chiave
3. **Corsa/Crepace** (10-20% importanza) - stamina, acceleration
4. **Aereo** (5-10% importanza) - aerial reach, jumping reach

### Valutazione Pesi Attuali vs Best Practice
| Aspetto | Pesi Attuali | Best Practice FM | Verdetto |
|---------|--------------|------------------|----------|
| Bilanciamento Difesa/Creatività | 24% / 51% | ~40% / ~40% | ⚠️ **Sbilanciato** - creatività troppo pesanti |
| Peso Key Passes (3.0) | Il più alto | Dovrebbe essere ~2.5 | ⚠️ **Eccessivo** |
| Peso xG per 90 (1.0) | Basso | Corretto (~1.0) | ✅ Appropriato |
| Penalità errori (-2.0) | Alta | Corretta (~-2.0) | ✅ Appropriato |
| Header Win % (1.5) | Medio | Dovrebbe essere ~2.0 per terzini alti | ⚠️ **Leggermente basso** |

---

## 5. Anomalie e Discrepanze Rilevate

### 🔴 ANOMALIA 1: Key Passes per 90 ha peso eccessivo (3.0)
- **Problema:** È la metrica con il peso più alto, superando anche Defensive Actions (2.5)
- **Impatto:** I terzini saranno valutati troppo come playmaker, non come difensori
- **Raccomandazione:** Ridurre a 2.5 per bilanciare con Defensive Actions

### 🟡 ANOMALIA 2: Squilibrio Difesa vs Creatività
- **Problema:** La creatività ha peso totale 16.3 contro 7.8 della difesa (2.1x)
- **Impatto:** Un terzino creativo ma difensivamente debole sarà premiato eccessivamente
- **Raccomandazione:** Aumentare pesi difensivi o ridurre quelli creativi

### 🟡 ANOMALIA 3: Header Win % sottopesato (1.5)
- **Problema:** I terzini moderni devono vincere molti duel aerei
- **Impatto:** Terzini alti e forti aereo non sono sufficientemente premiati
- **Raccomandazione:** Aumentare a 2.0

### 🟢 NOTE POSITIVE
1. ✅ xG per 90 ha peso basso (1.0) - corretto per terzini
2. ✅ xG Overperformance ha peso minimo (0.5) - evita rumore statistico
3. ✅ Mistakes Leading to Goals ha penalità alta (-2.0) - appropriato
4. ✅ Crosses Completed ha peso alto (2.5) - ruolo chiave del terzino

---

## 6. Schema Riassuntivo dei Pesi Consigliati

```python
FULLBACK_WEIGHTS_CONSIGLIATI = {
    # Difesa - aumentare leggermente
    "Defensive Actions per 90": 2.8,      # +0.3
    "Possession Won per 90": 2.2,         # +0.2
    "Blocks per 90": 2.0,                 # +0.2
    "Pressures Attempted per 90": 1.7,    # +0.2
    
    # Creatività - ridurre Key Passes
    "xA per 90": 2.5,                     # invariato
    "Key Passes per 90": 2.5,             # -0.5 (da 3.0)
    "Progressive Passes per 90": 2.0,     # invariato
    "Progressive Pass %": 2.5,            # invariato
    "Open Play Cross Completion %": 1.8,  # invariato
    "Clear Cut Chances Created": 2.0,     # invariato
    "Crosses Completed": 2.5,             # invariato
    
    # Attacco - aumentare Header Win
    "Dribbles per 90": 1.5,               # invariato
    "Goal Contributions per 90": 1.5,     # invariato
    "xG per 90": 1.0,                     # invariato
    "xG Overperformance": 0.5,            # invariato
    "Header Win %": 2.0,                  # +0.5
    
    # Negativa - invariata
    "Mistakes Leading to Goals": -2.0     # invariato
}
```

### Nuovo Bilanciamento Consigliato
```
DIFESA:      ~8.7   (27%)  ████████░░░░░░░░░░░░
CREATIVITÀ: 15.8   (49%)  ██████████████████░░
ATTACCO:    6.5    (20%)  ██████░░░░░░░░░░░░░░
NEGATIVA:   2.0    (6%)   ██░░░░░░░░░░░░░░░░░░
```

---

## 7. Conclusioni

### PUNTI DI FORZA
1. ✅ Struttura generale dei pesi è ragionevole
2. ✅ Metriche difensive hanno peso adeguato
3. ✅ Penalità errori è appropriata
4. ✅ xG e overperformance sono sottopesati correttamente

### CRITICITÀ PRINCIPALI
1. 🔴 **Key Passes per 90** ha peso eccessivo (3.0) - dovrebbe essere 2.5
2. 🟡 **Squilibrio Difesa/Creatività** - la creatività domina troppo (51% vs 24%)
3. 🟡 **Header Win %** leggermente sottopesato (1.5 vs 2.0 consigliato)

### AZIONI RACCOMANDATE
1. Ridurre `Key Passes per 90` da 3.0 a 2.5
2. Aumentare leggermente i pesi difensivi (+0.2 ciascuno)
3. Aumentare `Header Win %` da 1.5 a 2.0
