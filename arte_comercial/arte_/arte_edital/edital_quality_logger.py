"""
ARTE Edital Quality Logger v1.0
Rastreia a qualidade do pipeline de ingestão de editais.

Métricas por etapa:
  01_ingestao: ZIPs processados, PDFs encontrados, RelacaoItens extraídas
  04_pipeline: Tabelas Camelot, linhas extraídas, taxa completude TR
  05_joint:    Itens no summary, itens no master, taxa de rejeição

Uso:
  python edital_quality_logger.py          → Relatório completo
  python edital_quality_logger.py --json   → Exporta JSON
"""

import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(r"C:\Users\pietr\OneDrive\.vscode\arte_\DOWNLOADS")
EDITAIS_DIR = BASE_DIR / "EDITAIS"
# Tática Chumbo: Salvando os relatórios direto no Google Drive para Live Sync do NotebookLM
LOGS_DIR = Path(r"I:\Meu Drive\GoogleAI\ARTE_CI\metrics_edital")
SUMMARY_PATH = BASE_DIR / "summary.xlsx"
MASTER_PATH = BASE_DIR / "master.xlsx"


def scan_editais() -> dict:
    """Escaneia a pasta EDITAIS e gera métricas de qualidade."""
    if not EDITAIS_DIR.exists():
        return {"error": f"Pasta não encontrada: {EDITAIS_DIR}"}

    pastas = [d for d in EDITAIS_DIR.iterdir() if d.is_dir()]
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_editais": len(pastas),
        "editais": [],
        "totals": {
            "com_relacao_itens": 0,
            "com_termo_referencia": 0,
            "com_itens_xlsx": 0,
            "com_referencia_xlsx": 0,
            "com_master_xlsx": 0,
            "bugs": [],
        }
    }

    for pasta in sorted(pastas):
        nome = pasta.name
        
        # Detecta artefatos
        tem_relacao = any(
            f.name.lower().startswith("relacaoitens") and f.suffix.lower() == ".pdf"
            for f in pasta.iterdir() if f.is_file()
        )
        tem_tr = (pasta / "termo_referencia.pdf").exists()
        tem_itens = (pasta / f"{nome}_itens.xlsx").exists()
        tem_ref = (pasta / f"{nome}_referencia.xlsx").exists()
        tem_master = (pasta / f"{nome}_master.xlsx").exists()
        
        # Conta PDFs totais
        pdfs = [f for f in pasta.iterdir() if f.suffix.lower() == ".pdf"]
        
        # Detecta bugs
        bugs = []
        if not tem_relacao:
            bugs.append("SEM_RELACAO_ITENS")
        if not tem_tr and len(pdfs) <= 1:
            bugs.append("SEM_TERMO_REFERENCIA")
        if tem_itens and not tem_ref:
            bugs.append("ITENS_SEM_REFERENCIA")
        if tem_ref and not tem_itens:
            bugs.append("REFERENCIA_SEM_ITENS")
        if tem_itens and tem_ref and not tem_master:
            bugs.append("MERGE_NAO_EXECUTADO")
        
        # Verifica qualidade do _referencia.xlsx
        ref_quality = None
        if tem_ref:
            try:
                import pandas as pd
                df = pd.read_excel(pasta / f"{nome}_referencia.xlsx")
                total_rows = len(df)
                empty_ref = df["REFERENCIA"].isna().sum() if "REFERENCIA" in df.columns else total_rows
                ref_quality = {
                    "total_rows": total_rows,
                    "empty_refs": int(empty_ref),
                    "completude_pct": round((1 - empty_ref / total_rows) * 100, 1) if total_rows > 0 else 0
                }
                if ref_quality["completude_pct"] < 50:
                    bugs.append(f"BAIXA_COMPLETUDE_TR ({ref_quality['completude_pct']}%)")
            except Exception:
                bugs.append("ERRO_LEITURA_REFERENCIA")

        edital_data = {
            "nome": nome,
            "pdfs": len(pdfs),
            "relacao_itens": tem_relacao,
            "termo_referencia": tem_tr,
            "itens_xlsx": tem_itens,
            "referencia_xlsx": tem_ref,
            "master_xlsx": tem_master,
            "ref_quality": ref_quality,
            "bugs": bugs,
        }
        report["editais"].append(edital_data)

        # Totais
        if tem_relacao: report["totals"]["com_relacao_itens"] += 1
        if tem_tr: report["totals"]["com_termo_referencia"] += 1
        if tem_itens: report["totals"]["com_itens_xlsx"] += 1
        if tem_ref: report["totals"]["com_referencia_xlsx"] += 1
        if tem_master: report["totals"]["com_master_xlsx"] += 1
        report["totals"]["bugs"].extend(bugs)

    # Calcula taxas
    t = report["total_editais"]
    if t > 0:
        report["taxa_tr"] = round(report["totals"]["com_termo_referencia"] / t * 100, 1)
        report["taxa_master"] = round(report["totals"]["com_master_xlsx"] / t * 100, 1)
    else:
        report["taxa_tr"] = 0
        report["taxa_master"] = 0

    report["total_itens"] = report["totals"]["com_itens_xlsx"]
    
    return report


def quick_status() -> dict:
    """Retorna um dict mínimo para o daemon pulse (rápido, sem pandas)."""
    if not EDITAIS_DIR.exists():
        return {"total_editais": 0, "total_itens": 0, "taxa_tr": 0}

    pastas = [d for d in EDITAIS_DIR.iterdir() if d.is_dir()]
    total = len(pastas)
    
    com_tr = sum(1 for p in pastas if (p / "termo_referencia.pdf").exists())
    com_master = sum(1 for p in pastas if (p / f"{p.name}_master.xlsx").exists())
    
    # Conta itens no master.xlsx global se existir
    total_itens = "?"
    if MASTER_PATH.exists():
        try:
            import pandas as pd
            df = pd.read_excel(MASTER_PATH)
            total_itens = len(df)
        except Exception:
            pass
    
    return {
        "total_editais": total,
        "total_itens": total_itens,
        "taxa_tr": round(com_tr / total * 100, 1) if total > 0 else 0,
        "taxa_master": round(com_master / total * 100, 1) if total > 0 else 0,
    }


def print_report(report: dict):
    """Imprime relatório visual."""
    print("\n" + "═" * 70)
    print("  📄 ARTE EDITAL QUALITY REPORT")
    print("═" * 70)

    t = report["totals"]
    total = report["total_editais"]

    print(f"\n  Total Editais:     {total}")
    print(f"  Com RelacaoItens:  {t['com_relacao_itens']}/{total}")
    print(f"  Com TR Encontrado: {t['com_termo_referencia']}/{total} ({report['taxa_tr']}%)")
    print(f"  Com _itens.xlsx:   {t['com_itens_xlsx']}/{total}")
    print(f"  Com _ref.xlsx:     {t['com_referencia_xlsx']}/{total}")
    print(f"  Com _master.xlsx:  {t['com_master_xlsx']}/{total} ({report['taxa_master']}%)")

    # Bugs
    bugs = t["bugs"]
    if bugs:
        from collections import Counter
        bug_counts = Counter(bugs)
        print(f"\n  🐛 BUGS DETECTADOS: {len(bugs)}")
        for bug, count in bug_counts.most_common():
            print(f"     → {bug}: {count}x")

    # Editais com problemas
    problematicos = [e for e in report["editais"] if e["bugs"]]
    if problematicos:
        print(f"\n  ⚠️  EDITAIS COM PROBLEMAS ({len(problematicos)}):")
        for e in problematicos[:10]:
            print(f"     → {e['nome'][:40]}: {', '.join(e['bugs'])}")

    print("═" * 70)


def save_report(report: dict):
    """Salva relatório em formato estruturado Markdown para NotebookLM."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y_%m_%d")
    filepath = LOGS_DIR / f"quality_{ts}.md"
    
    t = report["totals"]
    
    md_lines = [
        f"# ARTE CI — Edital Quality Report",
        f"**Gerado em:** {report['timestamp']}",
        "",
        f"## Totais do Dia",
        f"- **Total de Editais Processados:** {report['total_editais']}",
        f"- **Com RelacaoItens:** {t['com_relacao_itens']} / {report['total_editais']}",
        f"- **Com Termo de Referência:** {t['com_termo_referencia']} / {report['total_editais']} ({report.get('taxa_tr', 0)}%)",
        f"- **Com _master.xlsx:** {t['com_master_xlsx']} / {report['total_editais']} ({report.get('taxa_master', 0)}%)",
        "",
        "## Bugs Globais Encontrados"
    ]
    
    bugs = t.get("bugs", [])
    if bugs:
        from collections import Counter
        bug_counts = Counter(bugs)
        for bug, count in bug_counts.most_common():
            md_lines.append(f"- **{bug}**: {count}x")
    else:
        md_lines.append("- Nenhum bug estrutural global detectado.")
        
    md_lines.append("")
    md_lines.append("## Detalhamento de Editais Problemáticos")
    
    problematicos = [e for e in report.get("editais", []) if e.get("bugs")]
    if problematicos:
        for e in problematicos:
            md_lines.append(f"### Edital: `{e['nome']}`")
            md_lines.append(f"- **PDFs encontrados:** {e['pdfs']}")
            for bug in e['bugs']:
                md_lines.append(f"  - 🐛 {bug}")
            if e.get('ref_quality'):
                md_lines.append(f"  - Qualidade TR: {e['ref_quality']['completude_pct']}% completude ({e['ref_quality']['empty_refs']} referências vazias)")
            md_lines.append("")
    else:
        md_lines.append("- Todos os editais foram processados 100% sem bugs estruturais registrados.")
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    
    print(f"💾 Relatório MD salvo em: {filepath}")
    return filepath


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ARTE Edital Quality Logger")
    parser.add_argument("--json", action="store_true", help="Salva relatório em MD (mantido flag --json p/ CI retrocompatível)")
    args = parser.parse_args()

    report = scan_editais()
    if "error" not in report:
        print_report(report)
        if args.json:
            save_report(report)
    else:
        print(f"❌ {report['error']}")
