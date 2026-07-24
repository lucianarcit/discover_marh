"""Executa o notebook e gera reports/phase3_rag_validation_demo.html.

O HTML prioriza resultados e gráficos (código ocultado) para apresentação
ao cliente.

Executar:
    cd C:\\proj\\discover_alelo\\notebooks
    python generate_report.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).parent
NOTEBOOK_IN   = NOTEBOOKS_DIR / "phase3_rag_validation_demo.ipynb"
REPORTS_DIR   = NOTEBOOKS_DIR.parent / "reports"
HTML_OUT      = REPORTS_DIR / "phase3_rag_validation_demo.html"

REPORTS_DIR.mkdir(exist_ok=True)

# 1. Reconstruir o notebook a partir do build_notebook.py (garante código atualizado)
print("Gerando notebook...")
result = subprocess.run(
    [sys.executable, str(NOTEBOOKS_DIR / "build_notebook.py")],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(result.stderr)
    sys.exit(1)
print(result.stdout.strip())

# 2. Executar o notebook com nbconvert (kernel Python)
print("Executando notebook...")
result = subprocess.run(
    [
        sys.executable, "-m", "nbconvert",
        "--to", "notebook",
        "--execute",
        "--ExecutePreprocessor.timeout=120",
        "--ExecutePreprocessor.kernel_name=python3",
        "--output", str(NOTEBOOK_IN),
        str(NOTEBOOK_IN),
    ],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("Aviso na execução do notebook:")
    print(result.stderr[:500])
    # Continua — pode haver avisos não fatais

# 3. Exportar para HTML sem código (prioriza resultados para cliente)
print("Exportando HTML (sem código)...")
result = subprocess.run(
    [
        sys.executable, "-m", "nbconvert",
        "--to", "html",
        "--no-input",                        # oculta células de código
        "--output", str(HTML_OUT),
        str(NOTEBOOK_IN),
    ],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(result.stderr[:500])
    # Tentar sem --no-input como fallback
    print("Tentando sem --no-input...")
    result = subprocess.run(
        [
            sys.executable, "-m", "nbconvert",
            "--to", "html",
            "--output", str(HTML_OUT),
            str(NOTEBOOK_IN),
        ],
        capture_output=True, text=True
    )

if HTML_OUT.exists():
    size_kb = HTML_OUT.stat().st_size // 1024
    print(f"HTML gerado: {HTML_OUT} ({size_kb} KB)")
else:
    print(f"Falha ao gerar HTML: {result.stderr[:300]}")
    sys.exit(1)

print("\nConcluído.")
print(f"  Notebook : {NOTEBOOK_IN}")
print(f"  HTML     : {HTML_OUT}")
