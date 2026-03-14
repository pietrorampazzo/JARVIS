"""
COS — Score Engine v3.0 (Moving Average & 30 Strategies)
Calcula a performance diária com base em média móvel competitiva.
"""

import json
import sys
import os
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List

# Setup caminhos
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from engine.shared.shared import get_config, get_today_log, load_json, LOGS_DIR, get_latest_snapshot
from engine.logic import inventory_engine
import pandas as pd

# Arquivo de histórico
HISTORY_FILE = LOGS_DIR / "score_history.json"

class ScoreEngineV3:
    def __init__(self):
        self.points_config = {
            "delta_proposals": 15,       # por nova proposta (Drive)
            "triagem_progress": 1,       # por item movido M->H
            "triagem_ultra": 2,          # por item movido H->U
            "commit_jarvis": 10,         # por commit jarvis
            "commit_project": 15,        # por commit arte/wappi
            "task_done": 5,              # por task [x]
            "bug_fixed": 20,             # tag #bug
            "deploy_major": 50,          # deploy site/bot
            "volume_heavy_50k": 1,       # cada 50k no heavy
            "volume_ultra_20k": 2,       # cada 20k no ultra
            "trello_move": 10,           # card movido p/ estágio final
            "pipeline_clean": 10,        # compras.gov zerado
            "focus_bonus": 10,           # log gap < 2h
            "multiproject": 5,           # 3+ projetos no dia
            "early_bird": 5,             # log antes das 09h
            "night_owl": 5,              # log após as 18h
            "refactor": 5,               # commit com 5+ arquivos
            "lead_capture": 5,           # novo lead no supabase
            "conversion": 30,            # card p/ GANHO
            "briefing_usage": 5,         # rodar cos_briefing
            "ocr_success": 5,            # extração OCR ok
            "data_audit": 10,            # correção excel
            "doc_update": 10,            # atualização walkthrough
            "health_log": 5,             # log exercício/descanso
            "networking": 10,            # log reunião
            "matching_growth": 10,       # +5% aproveitamento
            "infra_health": 10,          # pulse sem erros
            "oracle_usage": 5,           # consulta oráculo
            "task_edit": 5,              # atualizou task.md
            "bot_automation": 10,         # envio bot ok
            "nova_habilitada": 15,        # por novo card em HABILITADO vs ontem
            "edital_processado": 10,      # manual/download de edital
            "orcamento_gerado": 20        # arquivo de orçamento local
        }

    def get_history(self) -> Dict:
        if not HISTORY_FILE.exists():
            return {}
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def save_to_history(self, day_data: Dict):
        history = self.get_history()
        history[day_data["date"]] = {
            "total_pts": day_data["total_pts"],
            "metrics": day_data["metrics"]
        }
        # Mantém apenas os últimos 30 dias para não inflar
        sorted_dates = sorted(history.keys(), reverse=True)[:30]
        trimmed_history = {d: history[d] for d in sorted_dates}
        
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(trimmed_history, f, ensure_ascii=False, indent=2)

    def calculate_moving_average(self, days: int = 7) -> float:
        history = self.get_history()
        if not history:
            return 50.0 # Valor base se não houver histórico
        
        scores = [v["total_pts"] for v in history.values()]
        recent_scores = scores[:days]
        return sum(recent_scores) / len(recent_scores)

    def get_git_metrics(self) -> Dict:
        metrics = {"commits_jarvis": 0, "commits_project": 0, "refactors": 0, "bugs": 0}
        try:
            # Commits últimas 24h
            git_cmd = ["git", "log", "--since='24 hours ago'", "--oneline", "--pretty=format:%s"]
            output = subprocess.check_output(git_cmd, encoding="utf-8").strip()
            if output:
                lines = output.splitlines()
                for msg in lines:
                    if "#bug" in msg.lower(): metrics["bugs"] += 1
                    # Nota: Isso é simplificado, teria que varrer cada projeto no config
                    metrics["commits_jarvis"] += 1 
            
            # Refactors (arquivos mudados)
            git_diff = ["git", "diff", "--name-only", "HEAD@{1 day ago}", "HEAD"]
            files = subprocess.check_output(git_diff, encoding="utf-8").strip()
            if files and len(files.splitlines()) > 5:
                metrics["refactors"] += 1
        except:
            pass
        return metrics

    def calculate_daily_points(self, target_date: date, skip_inventory: bool = False) -> Dict:
        pts = 0
        metrics = {}
        
        # 0. Lógica de Habilitados (Comparativo Histórico)
        try:
            trello_snap = get_latest_snapshot()
            if trello_snap and "cards_by_list" in trello_snap:
                current_hab = len(trello_snap["cards_by_list"].get("HABILITADO", []))
                metrics["habilitados_count"] = current_hab
                
                # Busca ontem no histórico
                history = self.get_history()
                yesterday = (target_date - timedelta(days=1)).isoformat()
                if yesterday in history:
                    prev_hab = history[yesterday].get("metrics", {}).get("habilitados_count", 0)
                    new_hab = max(0, current_hab - prev_hab)
                    if new_hab > 0:
                        pts += new_hab * self.points_config["nova_habilitada"]
                        metrics["novas_habilitadas"] = new_hab
        except:
            pass

        # 1. Delta Inventário (Propostas, Editais e Orçamentos)
        if not skip_inventory:
            inventory_snap = inventory_engine.run_inventory()
            prev_inv_path = inventory_engine.find_previous_snapshot()
            if prev_inv_path:
                with open(prev_inv_path, "r", encoding="utf-8") as f:
                    prev_inv = json.load(f)
                delta_inv = inventory_engine.calculate_delta(inventory_snap, prev_inv)
                
                # Pontuação por Propostas (Drive)
                drive_files = [f for f in delta_inv["new_files"] if "DRIVE" in f or "ARTE" in f or "PIEZZO" in f]
                new_props = len(drive_files)
                if new_props > 0:
                    pts += new_props * self.points_config["delta_proposals"]
                    metrics["propostas_novas"] = new_props
                
                # Pontuação por Editais (Local)
                edital_files = [f for f in delta_inv["new_files"] if "EDITAIS" in f or "_itens.xlsx" in f or "_master.xlsx" in f]
                new_editais = len(edital_files)
                if new_editais > 0:
                    pts += new_editais * self.points_config["edital_processado"]
                    metrics["editais_processados"] = new_editais

                # Pontuação por Orçamentos (Local Downloads)
                orcamento_files = [f for f in delta_inv["new_files"] if "DOWNLOADS" in f and (".xlsx" in f or ".pdf" in f)]
                new_orcamentos = len(orcamento_files)
                if new_orcamentos > 0:
                    pts += new_orcamentos * self.points_config["orcamento_gerado"]
                    metrics["orcamentos_gerados"] = new_orcamentos
        else:
            metrics["inventory_skipped"] = True

        # 2. Triagem e UIDs
        try:
            projects_config = get_config("projects")
            arte_path = next((Path(p["path"]) for p in projects_config["projects"] if p["id"] == "arte_"), None)
            if arte_path:
                downloads = arte_path / "DOWNLOADS"
                m_path = downloads / "master.xlsx"
                h_path = downloads / "master_heavy.xlsx"
                u_path = downloads / "master_heavy_ultra.xlsx"
                
                # UID Logic Robusta (V3)
                uids_total = set()
                for path in [h_path, u_path]:
                    if path.exists():
                        try:
                            df_tmp = pd.read_excel(path, nrows=5)
                            cols = df_tmp.columns.tolist()
                            c_arq = "ARQUIVO" if "ARQUIVO" in cols else None
                            c_item = "Nº" if "Nº" in cols else ("ITEM" if "ITEM" in cols else None)
                            
                            if c_item:
                                use_cols = [c_item]
                                if c_arq: use_cols.append(c_arq)
                                df = pd.read_excel(path, usecols=use_cols)
                                if c_arq:
                                    df["uid"] = df[c_arq].astype(str) + "_" + df[c_item].astype(str)
                                else:
                                    df["uid"] = path.name + "_" + df[c_item].astype(str)
                                uids_total.update(df["uid"].dropna().tolist())
                        except:
                            pass
                
                if m_path.exists():
                    df_m_tmp = pd.read_excel(m_path, nrows=5)
                    c_arq_m = "ARQUIVO" if "ARQUIVO" in df_m_tmp.columns else None
                    c_item_m = "Nº" if "Nº" in df_m_tmp.columns else ("ITEM" if "ITEM" in df_m_tmp.columns else None)
                    
                    if c_item_m:
                        use_cols_m = [c_item_m]
                        if c_arq_m: use_cols_m.append(c_arq_m)
                        df_m = pd.read_excel(m_path, usecols=use_cols_m)
                        if c_arq_m:
                            df_m["uid"] = df_m[c_arq_m].astype(str) + "_" + df_m[c_item_m].astype(str)
                        else:
                            df_m["uid"] = "master_" + df_m[c_item_m].astype(str)
                        
                        uids_m = set(df_m["uid"].dropna().tolist())
                        triados = len(uids_m.intersection(uids_total))
                        
                        metrics["triados_count"] = triados
                        metrics["total_master"] = len(df_m)
                        pts += (triados * self.points_config["triagem_progress"])
                
                metrics["items_ultra"] = len(uids_total)
                pts += (len(uids_total) * self.points_config["triagem_ultra"])
        except:
            pass

        # 3. Logs e Tasks
        logs = get_today_log() if target_date == date.today() else []
        metrics["logs_count"] = len(logs)
        pts += len(logs) * 10 # 10 pts por log padrão
        
        # 4. Git
        git = self.get_git_metrics()
        pts += git["commits_jarvis"] * self.points_config["commit_jarvis"]
        pts += git["bugs"] * self.points_config["bug_fixed"]
        
        return {"total_pts": pts, "metrics": metrics, "date": target_date.isoformat()}

    def run(self, skip_inventory: bool = False):
        today = date.today()
        daily_data = self.calculate_daily_points(today, skip_inventory=skip_inventory)
        self.save_to_history(daily_data)
        
        avg = self.calculate_moving_average()
        performance = (daily_data["total_pts"] / avg) if avg > 0 else 1.0
        
        status = "⚖️ NA MÉDIA"
        if performance > 1.2: status = "🚀 ACIMA DA MÉDIA"
        elif performance < 0.8: status = "📉 ABAIXO DA MÉDIA"
        
        result = {
            **daily_data,
            "moving_average": round(avg, 1),
            "performance_ratio": round(performance, 2),
            "status": status,
            "emoji": "🔥" if performance > 1.0 else "❄️"
        }
        return result

def calculate_daily_score(target_date: Optional[date] = None, skip_inventory: bool = False):
    # Proxy para manter compatibilidade
    engine = ScoreEngineV3()
    
    # Se for uma data retroativa, OBRIGATORIAMENTE pula o inventory real
    # e tenta buscar do histórico se existir.
    if target_date and target_date != date.today():
        history = engine.get_history()
        date_str = target_date.isoformat()
        if date_str in history:
            # Retorna dados do histórico formatados para o legacy
            h_val = history[date_str]
            return {
                "global_score": h_val["total_pts"],
                "classification": "HISTÓRICO",
                "emoji": "📜",
                "moving_average": 0,
                "performance_ratio": 1.0,
                "metrics": h_val["metrics"],
                "areas": {} # legacy dummy
            }
        skip_inventory = True

    data = engine.run(skip_inventory=skip_inventory)
    
    # Mapeia métricas para áreas legadas para evitar KeyErrors
    m = data["metrics"]
    areas_legacy = {
        "economic_output": {"score": m.get("propostas_novas", 0) * 15 + m.get("triados_count", 0)},
        "system_building": {"score": m.get("commits_jarvis", 0) * 10},
        "execution_discipline": {"score": m.get("logs_count", 0) * 5},
        "energy_body": {"score": m.get("health_log", 0) * 5},
        "relations_influence": {"score": m.get("networking", 0) * 10}
    }

    return {
        "global_score": data["total_pts"],
        "classification": f"{data['status']} ({data['performance_ratio']:.2f}x)",
        "emoji": data["emoji"],
        "moving_average": data["moving_average"],
        "performance_ratio": data["performance_ratio"],
        "areas": areas_legacy  # Backwards compatibility
    }

def print_report(data):
    print(f"\n{'='*40}")
    print(f"  🏆 JARVIS SCORE V3 — {data['date']}")
    print(f"{'='*40}")
    print(f"  Pontos Hoje:    {data['total_pts']} pts")
    print(f"  Média Móvel:    {data['moving_average']} pts")
    print(f"  Performance:    {data['performance_ratio']:.2f}x")
    print(f"  Status:         {data['status']}")
    print(f"{'='*40}\n")

if __name__ == "__main__":
    engine = ScoreEngineV3()
    res = engine.run()
    print_report(res)
