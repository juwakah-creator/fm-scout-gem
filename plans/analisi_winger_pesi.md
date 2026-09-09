# Analisi Pesi Statistici - Winger

## 1. Riepilogo Pesi Identificati

### 1.1 Funzione `calculate_offensive_score` (linee 82-172)

**PESI OFFENSIVI:**
| Statistica | Peso | Note |
|------------|------|------|
| Goal Contributions / 90 | 2.0x | Peso massimo |
| xG / 90 | 2.0x | Peso massimo |
| xA / 90 | 2.0x | Peso massimo |
| NP-xG / 90 | 1.5x | Aggiornato da 1.0 a 1.5 |
| Dribbling completati / 90 | 1.2x | [NUOVA] |
| Shots on Target / 90 | 1.0x | Peso standard |
| Key Passes / 90 | 1.0x | Peso standard |
| Attacking Actions / 90 | 1.0x | Peso standard |
| Passaggi progressivi / 90 | 1.0x | [NUOVA] |
| Cross riusciti / 90 | 1.0x | [NUOVA] - **PROBLEMA** |
| xG Overperformance | 0.5x | Ridotto da 2.0 a 0.5 |

**PESI DIFENSIVI:**
| Statistica | Peso | Note |
|------------|------|------|
| Pressures Attempted / 90 | 0.4x | [NUOVA] |
| Possession Won / 90 | 0.3x | [NUOVA] |
| Pressing Efficiency | 0.2x | [NUOVA] |
| Header Win % | 0.1x | Esistente |

---

### 1.2 Funzione `compute_dimension_scores` (linee 509-669)

**Dimensione 'finalizzazione':**
| Statistica | Peso | Note |
|------------|------|------|
| Goal Contributions per 90 | 2.0 | Coerente con calculate_offensive_score |
| xG per 90 | 1.5 | **INCOERENTE** - calculate_offensive_score usa 2.0 |
| Shots on Target per 90 | 1.0 | Coerente |
| xG Overperformance | 0.5 | Coerente |

**Dimensione 'creazione':**
| Statistica | Peso | Note |
|------------|------|------|
| xA per 90 | 2.0 | Coerente |
| Key Passes per 90 | 1.5 | **DIVERGENTE** - calculate_offensive_score usa 1.0 |
| Passaggi progressivi per 90 | 1.0 | Coerente |

**Dimensione 'pressing':**
| Statistica | Peso | Note |
|------------|------|------|
| Pressures Attempted per 90 | 1.0 | Peso normalizzato nella dimensione |
| Possession Won per 90 | 1.0 | Peso normalizzato nella dimensione |

**Dimensione 'difesa_aerea':**
| Statistica | Peso | Note |
|------------|------|------|
| Header Win % | 1.0 | Con default_value 50.0 |

---

## 2. Confronto con Best Practice per Winger in Football Manager

### 2.1 Ruolo dell'Esterno d'Attacco in FM

Un esterno d'attacco (winger) in Football Manager deve eccellere in:
1. **Velocità e accelerazione** - Non direttamente misurabile dalle statistiche disponibili
2. **Dribbling** - Fondamentale per superare l'avversario 1v1
3. **Crossing** - Statistica primaria per creare occasioni da gol
4. **Finalizzazione** - Capacità di concludere le occasioni create
5. **Tocco e controllo palla** - Importante per mantenere la possesso
6. **Visione di gioco e passaggi** - Per combinazioni in terza finale

### 2.2 Analisi Proporzionalità dei Pesi

#### ✅ CORRETTI:
- **Goal Contributions / 90 (2.0x)** - Peso appropriato, statistica chiave per valutare l'impatto offensivo
- **xG / 90 (2.0x)** - Peso appropriato per misurare la qualità delle occasioni da gol
- **xA / 90 (2.0x)** - Peso appropriato per misurare la creatività
- **NP-xG / 90 (1.5x)** - Peso ragionevole, statistica avanzata ma non primaria

#### ⚠️ PROBLEMATICI:
- **Cross riusciti / 90 (1.0x)** - **SOVRAVALUTATO BASSO!** Per un winger, il crossing è una delle abilità più importanti. Dovrebbe avere peso almeno 1.5x o 2.0x per riflettere l'importanza del ruolo.
- **Dribbling completati / 90 (1.2x)** - **LEGGERAMENTE BASSO!** Il dribbling è fondamentale per un esterno. Dovrebbe essere almeno 1.5x o 2.0x.
- **Key Passes / 90 (1.0x in calculate_offensive_score vs 1.5x in compute_dimension_scores)** - **INCOERENZA!** Le due funzioni usano pesi diversi per la stessa statistica.

#### ❌ CRITICI:
- **Incoerenza xG tra le due funzioni**: `calculate_offensive_score` usa 2.0x, `compute_dimension_scores` usa 1.5x per la dimensione 'finalizzazione'. Questo crea discrepanze nei punteggi finali.
- **NP-xG non incluso nelle dimensioni**: Statistica importante per valutare la qualità delle occasioni da gol senza penalità sui rigori.

---

## 3. Discrepanze e Anomalie Rilevate

### 3.1 Incoerenze tra Funzioni

| Statistica | calculate_offensive_score | compute_dimension_scores | Differenza |
|------------|---------------------------|--------------------------|------------|
| xG / 90 | 2.0x | 1.5 (dimensione finalizzazione) | **0.5x** |
| Key Passes / 90 | 1.0x | 1.5 (dimensione creazione) | **0.5x** |

### 3.2 Pesi Sottostimati per Ruolo Winger

| Statistica | Peso Attuale | Peso Suggerito | Motivazione |
|------------|--------------|----------------|-------------|
| Cross riusciti / 90 | 1.0x | **1.5-2.0x** | Crossing è abilità primaria per winger |
| Dribbling completati / 90 | 1.2x | **1.5-2.0x** | Dribbling è fondamentale per 1v1 |

### 3.3 Metriche Mancanti per Ruolo Winger

- **Passaggi chiave nella terza finale** - Non presente nel dataset
- **Progressive carries / 90** - Non presente (utile per valutare l'avanzamento palla)
- **Duelli vittoriosi in attacco / 90** - Non presente

---

## 4. Raccomandazioni

### 4.1 Correzioni Immediate

1. **Aumentare peso Cross riusciti / 90 a 1.5x o 2.0x** in `calculate_offensive_score`
2. **Aumentare peso Dribbling completati / 90 a 1.5x o 2.0x** in `calculate_offensive_score`
3. **Risolvere incoerenza xG**: Uniformare a 2.0x in entrambe le funzioni OPPURE a 1.5x in entrambe

### 4.2 Miglioramenti Proposti

1. **Aggiungere Cross riusciti alla dimensione 'creazione'** con peso 1.5-2.0x
2. **Uniformare tutti i pesi** tra `calculate_offensive_score` e `compute_dimension_scores`
3. **Considerare l'aggiunta di metriche specifiche** se disponibili nel dataset

### 4.3 Bilanciamento Finale Suggerito

```
PESI OFFENSIVI IDEALI PER WINGER:
- Goal Contributions / 90: 2.0x (mantenere)
- xG / 90: 2.0x (mantenere o ridurre a 1.5x per coerenza)
- xA / 90: 2.0x (mantenere)
- NP-xG / 90: 1.5x (mantenere)
- Dribbling completati / 90: 1.5-2.0x (aumentare da 1.2x)
- Cross riusciti / 90: 1.5-2.0x (aumentare da 1.0x)
- Shots on Target / 90: 1.0x (mantenere)
- Key Passes / 90: 1.0-1.5x (uniformare)
- Attacking Actions / 90: 1.0x (mantenere)
- Passaggi progressivi / 90: 1.0x (mantenere)
- xG Overperformance: 0.5x (mantenere ridotto)

PESI DIFENSIVI (mantenere bassi per winger offensivo):
- Pressures Attempted / 90: 0.4x (mantenere)
- Possession Won / 90: 0.3x (mantenere)
- Pressing Efficiency: 0.2x (mantenere)
- Header Win %: 0.1x (mantenere)
```

---

## 5. Conclusioni

Il file [`winger.py`](winger.py) presenta **due problemi principali**:

1. **Incoerenze tra le due funzioni** che calcolano i punteggi, con pesi diversi per le stesse statistiche
2. **Sottostimazione di statistiche chiave per il ruolo winger**, in particolare Crossing e Dribbling

I pesi difensivi sono correttamente bassi (0.1-0.4x) per non penalizzare giocatori offensivi, ma le metriche offensive specifiche per il ruolo devono essere rivalutate per riflettere meglio le esigenze tattiche di un esterno d'attacco.
