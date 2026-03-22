import json
import os
import re
import sys
import subprocess
import time
import pandas as pd
from pathlib import Path

# --- CONFIGURAÇÕES DE CAMINHO ---
ROOT_DIR = Path(__file__).resolve().parent.parent.parent # arte_comercial
DOWNLOADS_DIR = ROOT_DIR / "downloads"
MASTER_FILE = DOWNLOADS_DIR / "master.xlsx"
PROJ_DIR = DOWNLOADS_DIR
OUTPUT_FILE = DOWNLOADS_DIR / "master_heavy.xlsx"
LAST_ANSWER_FILE = DOWNLOADS_DIR / "last_answer.json"
SKILL_RUN_SCRIPT = Path(os.path.expanduser("~")) / ".antigravity" / "skills" / "notebooklm" / "scripts" / "run.py"
MARGIN_MULTIPLIER = 1.50


def clean_json_output(content):
    """
    Extrai o objeto JSON de uma string que pode conter ruido, eco da pergunta
    ou blocos de codigo markdown.
    """
    content = re.sub(r"```json\s*", "", content)
    content = re.sub(r"```\s*", "", content)

    try:
        start_idx = content.find("{")
        end_idx = content.rfind("}")
        if start_idx != -1 and end_idx != -1:
            return content[start_idx : end_idx + 1]
    except Exception:
        pass

    return content


def clean_number(value):
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).replace("R$", "").replace(" ", "").strip()
    if not text:
        return 0.0

    try:
        if "," in text and "." in text:
            text = text.replace(".", "").replace(",", ".")
        elif "," in text:
            text = text.replace(",", ".")
        return float(text)
    except ValueError:
        return 0.0


def normalize_output_dataframe(df):
    if df.empty:
        return df

    df = df.copy()
    if "QTDE" in df.columns and "VALOR_VENDA" in df.columns:
        qtde = df["QTDE"].apply(clean_number)
        valor_venda = df["VALOR_VENDA"].apply(clean_number)
        df["VALOR_VENDA_TOTAL"] = (qtde * valor_venda).round(2)

    cols = df.columns.tolist()
    if "VALOR_VENDA_TOTAL" in cols:
        cols = [col for col in cols if col != "VALOR_VENDA_TOTAL"]
        insert_at = cols.index("VALOR_VENDA") + 1 if "VALOR_VENDA" in cols else len(cols)
        cols.insert(insert_at, "VALOR_VENDA_TOTAL")
        df = df[cols]

    return df


def process_row(row):
    try:
        if os.path.exists(LAST_ANSWER_FILE):
            os.remove(LAST_ANSWER_FILE)

        referencia = str(row["REFERENCIA"])
        valor_unit = clean_number(row["VALOR_UNIT"])
        valor_meta = valor_unit * 0.70

        # Fallback para DESCRICAO se REFERENCIA for nula
        ref_query = referencia if (referencia.lower() != "nan" and referencia.strip() != "") else str(row.get("DESCRICAO", ""))
        ref_curta = ref_query[:800]
        query = f"BUSCA: {ref_curta} por ate {valor_meta:.2f}"

        print(f"\nProcessando item: {ref_curta[:100]}...")
        print(f"Query enviada: {query[:150]}...")

        cmd = [
            sys.executable,
            SKILL_RUN_SCRIPT,
            "ask_question.py",
            "--question",
            query,
        ]

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        subprocess.run(cmd, env=env, check=True, cwd=PROJ_DIR, timeout=300)

        if not os.path.exists(LAST_ANSWER_FILE):
            print(f"Erro: arquivo de resposta {LAST_ANSWER_FILE} nao foi gerado pela skill.")
            return None

        with open(LAST_ANSWER_FILE, "r", encoding="utf-8") as file:
            raw_content = file.read()

        json_str = clean_json_output(raw_content)
        data = json.loads(json_str)

        valor = clean_number(data.get("VALOR", 0.0))
        qtde = clean_number(row.get("QTDE", 1))
        valor_venda = round(valor * MARGIN_MULTIPLIER, 2)
        valor_venda_total = round(qtde * valor_venda, 2)

        result = row.to_dict()
        result.update(
            {
                "marca_modelo_edital": data.get("marca_modelo_edital", "-"),
                "STATUS": data.get("STATUS", ""),
                "marca_sugerida": data.get("marca_sugerida", ""),
                "modelo_sugerido": data.get("modelo_sugerido", ""),
                "VALOR": valor,
                "VALOR_VENDA": valor_venda,
                "VALOR_VENDA_TOTAL": valor_venda_total,
                "MARGEM_LUCRO": round(valor_venda - valor, 2),
                "LUCRO_TOTAL": valor_venda_total,
                "JUSTIFICATIVA_TECNICA": data.get("JUSTIFICATIVA_TECNICA", ""),
                "PARECER_JURIDICO_IMPUGNACAO": data.get("PARECER_JURIDICO_IMPUGNACAO", ""),
            }
        )

        return result

    except subprocess.TimeoutExpired:
        print("Erro: tempo limite de 5 minutos atingido para este item.")
        return None
    except Exception as exc:
        print(f"Erro ao processar linha: {exc}")
        return None


def main():
    if not os.path.exists(MASTER_FILE):
        print(f"Arquivo mestre {MASTER_FILE} nao encontrado.")
        return

    os.makedirs(PROJ_DIR, exist_ok=True)

    df_master = pd.read_excel(MASTER_FILE)
    results = []
    processed_refs = set()

    if os.path.exists(OUTPUT_FILE):
        try:
            df_existing = normalize_output_dataframe(pd.read_excel(OUTPUT_FILE))
            if "STATUS" in df_existing.columns:
                finished_items = df_existing[df_existing["STATUS"].notna() & (df_existing["STATUS"] != "")]
                # Cria UID (ARQUIVO + Nº) para os itens já concluídos
                processed_uids = set((df_existing["ARQUIVO"].astype(str) + "_" + df_existing["Nº"].astype(str)).tolist())

            results = df_existing.to_dict("records")
            print(f"Continuando: {len(processed_uids)} itens ja concluidos no arquivo de saida.")
        except Exception as exc:
            print(f"Aviso ao ler arquivo de saida: {exc}. Comecando do zero.")

    # Identifica o que falta baseado na chave composta
    df_master["UID"] = df_master["ARQUIVO"].astype(str) + "_" + df_master["Nº"].astype(str)
    to_process = df_master[~df_master["UID"].isin(processed_uids)]
    print(f"Itens pendentes para processar (UID unique): {len(to_process)}")

    for _, row in to_process.iterrows():
        res = process_row(row)
        if res:
            uid_str = str(row["UID"])
            # Remove se ja existia (update)
            results = [item for item in results if (str(item.get("ARQUIVO")) + "_" + str(item.get("Nº"))) != uid_str]
            results.append(res)

            normalize_output_dataframe(pd.DataFrame(results)).to_excel(OUTPUT_FILE, index=False)

            print("Item processado com sucesso. Aguardando 80 segundos...")
            time.sleep(80)
        else:
            print("Item falhou ou deu timeout. Pulando para o proximo para manter o fluxo.")
            time.sleep(10)

    print(f"\nProcessamento concluido ou interrompido. Verifique: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
