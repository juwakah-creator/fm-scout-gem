# Report Esaustivo - Statistiche Analizzate da FM Scout Gem

## 1. STATISTICHE DI INPUT (Metriche Grezze)

Il sistema analizza i seguenti dati provenienti dal file CSV:

### 1.1 Dati Anagrafici e di Mercato
| Statistica | Descrizione | Note |
|------------|-------------|------|
| **Name** | Nome del giocatore | Colonna obbligatoria |
| **Club** | Squadra di appartenenza | Colonna obbligatoria |
| **Age** | Età del giocatore | Colonna obbligatoria, usata per il fattore età |
| **Guide Value** | Valore di mercato (guida) | Formato: €1.2M, €50K, ecc. |
| **Appearances** | Presenze in stagione | Usato come filtro minimo |

### 1.2 Metriche Offensive Per 90 Minuti
| Statistica | Simbolo | Descrizione Tecnica |
|------------|---------|---------------------|
| **Goal Contributions per 90** | G+A/90 | Somma di gol e assist realizzati per ogni 90 minuti giocati |
| **xG per 90** | xG/90 | Expected Goals - quantità di occasioni da gol create per 90 minuti |
| **xA per 90** | xA/90 | Expected Assists - qualità delle occasioni da assist create per 90 minuti |
| **Shots on Target per 90** | SoT/90 | Tiri in porta realizzati per ogni 90 minuti |
| **Key Passes per 90** | KP/90 | Passaggi decisivi che creano occasioni da gol per 90 minuti |
| **Attacking Actions per 90** | AA/90 | Somma di passaggi chiave, tiri e dribbling offensivi per 90 minuti |
| **NP-xG per 90** | NP-xG/90 | Expected Goals senza rigori - misura la qualità dei gol reali per 90 minuti |
| **xG Overperformance** | xG OVP | Differenza tra gol realizzati e xG atteso (misura di finishing luck/skill) |
| **Shots per 90** | S/90 | Totale tiri effettuati per ogni 90 minuti |

---

## 2. METRICHE CALCOLATE DAL SISTEMA

### 2.1 Offensive Score (Punteggio Offensivo Composito)
Il sistema calcola un punteggio offensivo ponderato che combina tutte le metriche sopra elencate.

**Formula:**
```
Offensive Score = Σ(Metrica_i × Peso_i) / Σ(Pesi)
```

### 2.2 Age Factor (Fattore Età)
Premia i giocatori giovani con moltiplicatori crescenti:

| Fascia d'Età | Fattore | Logica |
|--------------|---------|--------|
| Age < 20 | **2.0** | Youngest players - massimo bonus |
| 20 ≤ Age < 24 | **1.6** | Early 20s - alto potenziale sviluppo |
| 24 ≤ Age < 27 | **1.3** | Mid-20s - maturità sportiva |
| Age ≥ 27 | **1.0** | Nessun bonus età |

### 2.3 Value Index (Indice di Valore)
Metrica principale per identificare i migliori affari:

```
Value Index = (Offensive Score × Age Factor) / Guide Value
```

**Interpretazione:** Più alto è il Value Index, migliore è il rapporto qualità/prezzo considerando anche l'età.

### 2.4 Offensive Efficiency (Efficienza Offensiva)
Misura quanto un giocatore è efficiente nel convertire i tiri in azioni offensive:

```
Offensive Efficiency = Goal Contributions per 90 / Shots per 90
```

**Interpretazione:** Valore più alto indica maggiore efficienza nel finalizzare le occasioni create.

### 2.5 Growth Potential (Potenziale di Crescita)
Metrica secondaria che identifica giocatori sottoperformanti rispetto alle aspettative:

```
Growth Potential = xG per 90 (se xG > 0 e xG Overperformance < 0)
                 = 0.0 (altrimenti)
```

**Interpretazione:** Giocatori con alto xG ma overperformance negativa potrebbero essere vittime di sfortuna e destinati a migliorare.

---

## 3. SISTEMA DI PESATURA (Weights)

Il sistema utilizza pesi differenziati per metriche offensive (elevati) e difensive (moderati/bassi), standardizzati su per-90 minuti per garantire confrontabilità.

### 3.1 Metriche Offensive (Pesi Elevati: 0.5 - 2.0)

| Metrica | Peso | Categoria | Note/Logica del Peso | Status |
|---------|------|-----------|---------------------|--------|
| **Goal Contributions per 90** | **2.0x** | Offensiva | Pilastro offensivo - somma di gol e assist, massima predittività | Esistente |
| **xG per 90** | **2.0x** | Offensiva | Qualità di conclusione - expected goals come metrica fondamentale | Esistente |
| **xA per 90** | **2.0x** | Offensiva | Creazione occasioni - expected assists come metrica fondamentale | Esistente |
| **NP-xG per 90** | **1.5x** | Offensiva | xG non penalizzato (senza rigori) - indica finalizzazione pura | Esistente |
| **Dribbling completati per 90** | **1.2x** | Offensiva | Progressione individuale con il pallone - capacità di superare avversari | [NUOVA] |
| **Shots on Target per 90** | **1.0x** | Offensiva | Tiri in porta - precisione nel finalizzare le occasioni | Esistente |
| **Key Passes per 90** | **1.0x** | Offensiva | Passaggi decisivi che creano occasioni da gol | Esistente |
| **Attacking Actions per 90** | **1.0x** | Offensiva | Azioni offensive totali (passaggi chiave + tiri + dribbling) | Esistente |
| **Passaggi progressivi per 90** | **1.0x** | Offensiva | Progressione con il pallone attraverso le linee difensive | Esistente |
| **Cross riusciti per 90** | **1.0x** | Offensiva | Cross efficaci che portano a occasioni da gol | [NUOVA] |
| **xG Overperformance** | **0.5x** | Offensiva | Ridotto per evitare rumore statistico e sovrastima - differenza tra gol realizzati e xG atteso | Esistente (aggiornato) |

### 3.2 Metriche Difensive (Pesi Moderati/Bassi: 0.1 - 0.4)

| Metrica | Peso | Categoria | Note/Logica del Peso | Status |
|---------|------|-----------|---------------------|--------|
| **Pressures Attempted per 90** | **0.4x** | Difensiva | Intensità pressante - numero di pressioni attivate per 90 minuti | [NUOVA] |
| **Possession Won per 90** | **0.3x** | Difensiva | Recupero possesso - palloni recuperati in zona offensiva/difensiva | [NUOVA] |
| **Pressing Efficiency** | **0.2x** | Difensiva | Efficienza del pressing - rapporto tra possession won e pressures attempted | [NUOVA] |
| **Header Win %** | **0.1x** | Difensiva | Duello aereo - peso minimo per evitare distorsioni nei punteggi complessivi | Esistente (nuova categoria) |

### 3.3 Principi di Bilanciamento

- **Range offensive:** 0.5x - 2.0x (pesi elevati per massimizzare l'impatto predittivo)
- **Range difensive:** 0.1x - 0.4x (pesi moderati/bassi per evitare sovrappeso difensivo)
- **Standardizzazione:** Tutte le metriche sono normalizzate su per-90 minuti per garantire confrontabilità tra giocatori con diverso tempo di gioco
- **Equilibrio:** Il sistema privilegia le statistiche offensive (che hanno maggiore potere predittivo) mantenendo un contributo difensivo misurato ma non dominante

---

## 4. NORMALIZZAZIONE DEI DATI

Il sistema utilizza la **normalizzazione min-max** per rendere confrontabili le metriche:

```
Normalized Value = (Value - Min) / (Max - Min)
```

**Range risultato:** [0, 1] dove:
- 0 = valore minimo nel dataset
- 1 = valore massimo nel dataset

**Casi speciali:**
- Se tutti i valori sono uguali → normalizzato a 0.5
- Valori NaN rimangono NaN dopo la normalizzazione

---

## 5. FILTRI APPLICATI

Il sistema applica i seguenti filtri per selezionare i giocatori:

| Filtro | Condizione | Default |
|--------|------------|---------|
| **Prezzo Minimo** | Guide Value ≥ min_price | €0 |
| **Prezzo Massimo** | Guide Value ≤ price_threshold | €15M (default UI) |
| **Presenze Minime** | Appearances ≥ min_apps | 10 |
| **Età Massima** | Age < max_age | 30 anni |

---

## 6. FLUSSO DI ELABORAZIONE COMPLETO

```
1. Lettura CSV → Parsing Guide Value (€M, €K)
2. Rilevamento automatico colonne (alias matching)
3. Conversione metriche in numerico
4. Applicazione filtri (prezzo, età, presenze)
5. Normalizzazione min-max delle statistiche offensive
6. Calcolo Offensive Score ponderato
7. Calcolo Age Factor basato sull'età
8. Calcolo Value Index = (Offensive Score × Age Factor) / Prezzo
9. Calcolo Offensive Efficiency
10. Ordinamento per Value Index decrescente
11. Estrazione top 20 giocatori
12. Generazione output HTML con tabella Bootstrap
```

---

## 7. OUTPUT GENERATO

Il sistema produce un report HTML che include:

- **Colonne base:** Name, Club, Age, Guide Value
- **Metriche calcolate:** Offensive Score, Value Index, Age Factor, Offensive Efficiency
- **Statistiche offensive originali:** Tutte le metriche per 90 disponibili nel dataset

**Ordinamento:** I giocatori sono ordinati per **Value Index decrescente**, mostrando prima i migliori affari.

---

## 8. NOTE TECNICHE

### 8.1 Gestione Errori
- Valori mancanti (NaN) vengono gestiti con fallback a 0 o NaN
- Parsing errori su Guide Value generano warning e valore NaN
- Se meno di 3 colonne offensive sono trovate → errore "Insufficient offensive statistics"

### 8.2 Varianti Colonne Supportate
Il sistema riconosce alias per le colonne:
- **Name:** name, player, fullname, full_name, title
- **Club:** club, team, organization, company
- **Age:** age, years, duration
- **Guide Value:** value, price, guide_value, guide value, cost, worth
- **Appearances:** appearances, apps, games_played, playtime

### 8.3 Formati Valuta Supportati
- `€1.2M` → 1,200,000
- `€50K` → 50,000
- `€1200000` → 1,200,000 (formato diretto)

---

## 9. CONFRONTO TRA MODULI

| Aspetto | winger.py | scout_app.py |
|---------|---------------------|--------------|
| **Peso xG Overperformance** | 2.0 (bonus se > 0) | 0.5 |
| **Peso NP-xG** | 1.0 (standard) | 1.5 |
| **Normalizzazione** | Min-max su Offensive Score totale | Min-max su ogni metrica singolarmente |
| **Colonne richieste minime** | Nessuna specifica | Almeno 3 offensive columns |
| **Output** | CSV + print a console | HTML con Bootstrap table |

---

*Report generato automaticamente dall'analisi del codice sorgente FM Scout Gem*