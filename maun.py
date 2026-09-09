#!/usr/bin/env python3
"""Script di validazione per la guida toggle eta Gradio."""

import sys
import os
import re
import tempfile

def validate_guida_file():
    """Valida il contenuto del file guida."""
    
    print("=" * 60)
    print("VALIDAZIONE GUIDA TOGGLE ETA GRADIO")
    print("=" * 60)
    
    # Leggi il file guida
    with open("guida_toggle_eta_gradio.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    checks = []
    
    # 1. Verifica presenza di gr.Slider con range corretto
    if "gr.Slider" in content and "minimum=16" in content and "maximum=45" in content:
        checks.append("[OK] Slider presente con range 16-45")
    else:
        checks.append("[FAIL] Slider non trovato o range errato")
    
    # 2. Verifica presenza di default value 18
    if "value=18" in content or "DEFAULT_MIN_AGE = 18" in content:
        checks.append("[OK] Default min_age = 18")
    else:
        checks.append("[FAIL] Default min_age non trovato")
    
    # 3. Verifica assenza di gr.Checkbox (toggle rimosso)
    if "gr.Checkbox" not in content and "enable_min_age" not in content:
        checks.append("[OK] Nessun toggle/checkbox presente")
    else:
        checks.append("[WARN] Trovato ancora riferimento a checkbox/toggle")
    
    # 4. Verifica presenza di gr.Row e gr.Column
    if "gr.Row" in content and "gr.Column" in content:
        checks.append("[OK] Layout responsive con Row/Column presente")
    else:
        checks.append("[FAIL] Layout responsive non trovato")
    
    # 5. Verifica funzione process_with_min_age_filter
    if "def process_with_min_age_filter" in content:
        checks.append("[OK] Funzione process_with_min_age_filter presente")
    else:
        checks.append("[FAIL] Funzione process_with_min_age_filter non trovata")
    
    # 6. Verifica validazione input
    if "ValueError" in content and "TypeError" in content:
        checks.append("[OK] Gestione errori e validazione presenti")
    else:
        checks.append("[WARN] Gestione errori incompleta")
    
    # 7. Verifica integrazione con scout_app
    if "from scout_app import detect_columns, parse_value, normalize, age_factor" in content:
        checks.append("[OK] Import da scout_app presenti")
    else:
        checks.append("[WARN] Import scout_app non trovato")
    
    # 8. Verifica commenti in italiano
    italian_comments = ["Processa i dati", "Args:", "Returns:", "Raises:", "Validazione input"]
    if all(comment in content for comment in italian_comments):
        checks.append("[OK] Commenti in italiano presenti")
    else:
        checks.append("[WARN] Commenti incompleti")
    
    # 9. Verifica esempio eseguibile (accetta anche app.launch( con argomenti)
    has_main = "__main__" in content
    has_launch = "app.launch(" in content or "main()" in content
    if has_main and has_launch:
        checks.append("[OK] Esempio completo con entry point presente")
    else:
        checks.append("[FAIL] Esempio eseguibile non trovato")
    
    # 10. Verifica pattern Gradio 2024-2025
    if ".change()" in content and "inputs=" in content and "outputs=" in content:
        checks.append("[OK] Pattern eventi Gradio 2024-2025 presenti")
    else:
        checks.append("[WARN] Pattern eventi incompleti")
    
    print("\nRisultati validazione:")
    print("-" * 40)
    for check in checks:
        print(check)
    
    # Calcola punteggio
    passed = sum(1 for c in checks if c.startswith("[OK]"))
    total = len(checks)
    score = (passed / total) * 100
    
    print("-" * 40)
    print(f"Punteggio: {passed}/{total} ({score:.0f}%)")
    
    if score >= 80:
        print("\n[OK] VALIDAZIONE SUPERATA - Il file guida e pronto per l'uso!")
        return True
    else:
        print("\n[FAIL] VALIDAZIONE NON SUPERATA - Correggi gli errori sopra.")
        return False

def test_code_syntax():
    """Testa la sintassi del codice Python nel file."""
    print("\n" + "=" * 60)
    print("TEST SINTASSI CODICE PYTHON")
    print("=" * 60)
    
    import py_compile
    
    # Estrae i blocchi di codice Python dal markdown
    with open("guida_toggle_eta_gradio.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Trova tutti i blocchi ```python ... ```
    python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
    
    print(f"\nTrovati {len(python_blocks)} blocchi di codice Python")
    
    all_valid = True
    for i, block in enumerate(python_blocks, 1):
        # Rimuove indentazione e commenta le righe vuote
        code = block.strip()
        if not code:
            continue
            
        try:
            # Usa tempfile con encoding utf-8 per evitare problemi
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            
            py_compile.compile(tmp_path, doraise=True)
            os.unlink(tmp_path)
            print(f"[OK] Blocco {i}: sintassi valida")
        except py_compile.PyCompileError as e:
            # Stampa solo la parte ASCII dell'errore
            error_msg = str(e).encode('ascii', 'replace').decode('ascii')
            print(f"[FAIL] Blocco {i}: errore di sintassi - {error_msg}")
            all_valid = False
    
    if all_valid:
        print("\n[OK] Tutti i blocchi Python hanno sintassi valida!")
        return True
    else:
        print("\n[FAIL] Alcuni blocchi hanno errori di sintassi.")
        return False

if __name__ == "__main__":
    # Cambia directory al progetto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Esegue le validazioni
    guida_ok = validate_guida_file()
    syntax_ok = test_code_syntax()
    
    print("\n" + "=" * 60)
    print("RIEPILOGO FINALE")
    print("=" * 60)
    
    if guida_ok and syntax_ok:
        print("\n[TUTTO OK] Il file guida e pronto per essere usato!")
        sys.exit(0)
    else:
        print("\n[WARN] CORREZIONI NECESSARIE")
        sys.exit(1)
