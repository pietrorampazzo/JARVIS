"""
05_joint_master.py

Responsabilidade: 
1. Para cada subpasta de edital, criar um arquivo '{nome_pasta}_master.xlsx' 
   fazendo o merge de '{nome_pasta}_itens.xlsx' e '{nome_pasta}_referencia.xlsx'.
2. Consolidar todos os arquivos '*_master.xlsx' gerados.
3. Gerar 'summary.xlsx' com a união de TODOS os itens de todos os editais processados.
4. Gerar 'master.xlsx' com os itens filtrados por palavras-chave de interesse.
"""
import os
import re
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

# =====================================================================================
# 1. CONFIGURAÇÕES E CONSTANTES
# =====================================================================================

# --- Configurações de Caminhos ---
BASE_DIR = Path(r"C:\Users\pietr\OneDrive\.vscode\arte_\DOWNLOADS")
PASTA_EDITAIS = BASE_DIR / "EDITAIS"

# Arquivos de saída consolidados na pasta 'DOWNLOADS'
SUMMARY_EXCEL_PATH = BASE_DIR / "summary.xlsx"
FINAL_MASTER_PATH = BASE_DIR / "master.xlsx"

# Sufixos e nomes dos arquivos a serem processados em cada subpasta
ITENS_SUFFIX = "_itens.xlsx"
REFERENCIA_SUFFIX = "_referencia.xlsx"
MASTER_SUFFIX = "_master.xlsx"

# Configuração de logging
LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# --- Configurações de Filtro (Replicado de arte_edital.py) ---
PALAVRAS_CHAVE = [
    # ------------------ Categorias principais ------------------
    r'Instrumento Musical',r'Instrumento Musical - Sopro',r'Instrumento Musical - Corda',r'Instrumento Musical - Percussão',
    r'Peças e acessórios instrumento musical',
    r'Peças E Acessórios Instrumento Musical',
    r"Mesa áudio ", r"Processador Áudio"

    # ------------------ Sopros ------------------
    r'saxofone',r'trompete',r'tuba',r'clarinete',r'trompa', 
    r'óleo lubrificante', r'óleos para válvulas', r'Corneta Longa',

    # ------------------ Cordas ------------------
    r'violão',r'Guitarra',r'Violino',
    r'Viola',r'Cavaquinho',r'Bandolim',
    r'Ukulele', r'Violoncelo'

    # ------------------ Percussão ------------------
    r'tarol', r'Bombo', r'CAIXA TENOR', r'Caixa tenor', r'Caixa de guerra',
    r'Bateria completa', r'Bateria eletrônica',
    r'Pandeiro', r'Pandeiro profissional', 
    r'Atabaque', r'Congas', r'Timbau',
    r'Xilofone', r'Glockenspiel', r'Vibrafone',
    r'Tamborim', r'Reco-reco', r'Agogô', r'Chocalho',
    r'Prato de bateria', r'Prato de Bateria', r'TRIÂNGULO',
    r'Baqueta', r'Baquetas', r'PAD ESTUDO', r'QUADRITOM', 

    # ------------------ Teclas ------------------
    r'Piano', r"Mesa Áudio / Vídeo", r'Teclado Musical', 
    r'Suporte para teclado',

    # ------------------ Microfones e acessórios ------------------
    r'Microfone', r'palheta', r'PALHETA', r"Microfone Microfone",
    r'Microfone direcional', r'Microfone',
    r'Microfone Dinâmico',
    r'Microfone de Lapela',
    r'Suporte microfone',
    r'Base microfone',
    r'Medusa para microfone',
    r'Pré-amplificador microfone',
    r'Fone Ouvido', r'Gooseneck',
    r"Fone ouvido Fone Ouvido",

    # ------------------ Áudio (caixas, amplificação, interfaces) ------------------
    r'Caixa Acústica', r'Caixa de Som',
    r'Caixa de Som', r"ALTO-FALANTE",
    r'Caixa som', r'Sistema de Som',
    r'Subwoofer',
    r'Amplificador de áudio',
    r'Amplificador som',
    r'Amplificador fone ouvido',
    r'Interface de Áudio',
    r'Mesa áudio', r'Mesa de Som', 
    r'Equipamento Amplificador', r'Rack para Mesa'

    # ------------------ Pedestais e suportes ------------------
    r'Pedestal caixa acústica',
    r'Pedestal microfone',
    r'Estante - partitura',
    r'Suporte de videocassete',

    # ------------------ Projeção ------------------
    r'Tela projeção',
    r'Projetor Multimídia', r'PROJETOR MULTIMÍDIA', r'Projetor imagem',

    # ------------------ Efeitos ------------------
    r'drone', r'DRONE', r'Aeronave', r'Energia solar',
]
REGEX_FILTRO = re.compile('|'.join(PALAVRAS_CHAVE), re.IGNORECASE)

# --- Configurações de Exclusão (Replicado de arte_edital.py) ---
PALAVRAS_EXCLUIR = [
    r'notebook', r'Dosímetro Digital', r'Radiação',r'Raios X', r'Aparelho eletroestimulador', r'Armário', r'Aparelho ar',
    r'webcam', r'Porteiro Eletrônico', r'Alicate Amperímetro',r'multímetro', r'Gabinete Para Computador',
    r'Microcomputador', r'Lâmpada projetor', r'Furadeira', r'Luminária', r'Parafusadeira', r'Brinquedo em geral',
    r'Aparelho Telefônico', r'Decibelímetro', r'Termohigrômetro', r'Trenador', r'Balança Eletrônica', r'BATERIA DE LÍTIO',
    r'smart TV', r'bombona', r'LAMPADA', r'LUMINARIA', r'ortopedia', r'Calculadora eletrônica', r'Luz Emergência', r'Desfibrilador',
    r'Colorímetro', r'Peagâmetro', r'Rugosimetro', r'Nível De Precisão', r'Memória Flash', r'Fechadura Biometrica', r'Bateria Telefone',
    r'Testador Bateria', r'Analisador cabeamento', r'Termômetro', r'Sensor infravermelho', r'Relógio Material', r'Armário de aço',
    r'Serra portátil', r'Ultrassom', r'Bateria não recarregável', r'Arduino', r'ALICATE TERRÔMETRO'
    r'Lâmina laboratório', r'Medidor E Balanceador', r'Trena eletrônica', r'Acumulador Tensão', r'Sirene Multiaplicação', r'Clinômetro',
    r'COLETOR DE ASSINATURA', r'Localizador cabo', r'Laserpoint', r'Bateria Filmadora',
]
REGEX_EXCLUIR = re.compile('|'.join(PALAVRAS_EXCLUIR), re.IGNORECASE)

# --- Configurações de Exceção ao Filtro (Replicado de arte_edital.py) ---
PALAVRAS_EXCECAO = [
    r'drone', r'DRONE', r'Aeronave',
]
REGEX_EXCECAO = re.compile('|'.join(PALAVRAS_EXCECAO), re.IGNORECASE)


# =====================================================================================
# 2. FUNÇÕES PRINCIPAIS
# =====================================================================================
def _standardize_col_names(df: pd.DataFrame, potential_names: list, standardized_name: str) -> pd.DataFrame:
    """Renomeia a primeira coluna encontrada de uma lista para um nome padrão."""
    for name in potential_names:
        if name in df.columns:
            df.rename(columns={name: standardized_name}, inplace=True)
            logger.debug(f" > Coluna '{name}' padronizada para '{standardized_name}'.")
            return df
    logger.warning(f" > Nenhuma coluna de item ({potential_names}) encontrada. O merge pode falhar.")
    return df

def criar_master_individual(edital_dir: Path):
    """
    Cria o arquivo '{nome_pasta}_master.xlsx' a partir dos arquivos de itens e referência,
    lidando com nomes de colunas inconsistentes para o número do item.
    """
    nome_base = edital_dir.name
    itens_path = edital_dir / f"{nome_base}{ITENS_SUFFIX}"
    referencia_path = edital_dir / f"{nome_base}{REFERENCIA_SUFFIX}"
    master_path = edital_dir / f"{nome_base}{MASTER_SUFFIX}"

    if not itens_path.exists():
        logger.warning(f"Arquivo de itens não encontrado para o edital '{nome_base}'. Pulando.")
        return

    logger.info(f"Processando edital: {nome_base}")
    df_itens = pd.read_excel(itens_path)
    
    # Padroniza o nome da coluna de número do item
    df_itens = _standardize_col_names(df_itens, ['Nº', 'N'], 'Nro_Item')

    # Garante que a coluna de merge exista antes de prosseguir
    if 'Nro_Item' not in df_itens.columns:
        logger.error(f" > Impossível continuar sem uma coluna de número de item em '{itens_path.name}'.")
        df_itens.to_excel(master_path, index=False) # Salva o arquivo de itens como master para não quebrar o fluxo
        return
        
    df_itens['Nro_Item'] = df_itens['Nro_Item'].astype(str)

    # Se o arquivo de referência existir, faz o merge.
    if referencia_path.exists():
        df_referencia = pd.read_excel(referencia_path)
        df_referencia = _standardize_col_names(df_referencia, ['ITEM', 'Nº'], 'Nro_Item')
        
        if 'Nro_Item' in df_referencia.columns and 'REFERENCIA' in df_referencia.columns:
            df_referencia['Nro_Item'] = df_referencia['Nro_Item'].astype(str)
            
            df_master = pd.merge(
                df_itens, 
                df_referencia[['Nro_Item', 'REFERENCIA']], 
                on='Nro_Item', 
                how='left'
            )
            logger.info(f" > Merge realizado com sucesso para '{nome_base}'.")
        else:
            logger.warning(f" > Arquivo de referência para '{nome_base}' não contém colunas padronizadas. 'REFERENCIA' ficará vazia.")
            df_master = df_itens
            df_master['REFERENCIA'] = None
    else:
        logger.warning(f" > Arquivo de referência não encontrado para '{nome_base}'. 'REFERENCIA' ficará vazia.")
        df_master = df_itens
        df_master['REFERENCIA'] = None

    # Renomeia a coluna de número de item de volta para o padrão 'Nº'
    df_master.rename(columns={'Nro_Item': 'Nº'}, inplace=True)

    # Adiciona a coluna com o nome da subpasta de origem
    df_master['ARQUIVO'] = nome_base
    logger.debug(f" > Adicionada coluna 'ARQUIVO' com o valor '{nome_base}'.")


    # Reordena colunas para ter a REFERENCIA ao lado da DESCRICAO
    cols = list(df_master.columns)
    if 'DESCRICAO' in cols and 'REFERENCIA' in cols:
        cols.remove('REFERENCIA')
        if 'DESCRICAO' in cols:
            desc_index = cols.index('DESCRICAO')
            cols.insert(desc_index + 1, 'REFERENCIA')
        else:
            cols.append('REFERENCIA') # Adiciona no final se 'DESCRICAO' não existir
        df_master = df_master[cols]

    df_master.to_excel(master_path, index=False)
    logger.info(f" > Arquivo '{master_path.name}' salvo com sucesso.")


def encontrar_arquivos_master(pasta_editais: Path) -> list[Path]:
    """Encontra todos os arquivos '*_master.xlsx' nas subpastas de editais."""
    if not pasta_editais.is_dir():
        logger.error(f"O diretório de editais '{pasta_editais}' não foi encontrado.")
        return []
    
    files = list(pasta_editais.rglob(f"*{MASTER_SUFFIX}"))
    logger.info(f"Encontrados {len(files)} arquivos '{MASTER_SUFFIX}' para consolidação.")
    return files

def consolidar_dataframes(lista_arquivos: list[Path]) -> pd.DataFrame:
    """Carrega e concatena uma lista de arquivos Excel em um único DataFrame."""
    lista_dfs = []
    for f in lista_arquivos:
        try:
            # Garante que colunas importantes sejam lidas como string para evitar problemas de tipo
            df = pd.read_excel(f, dtype={'Nº': str, 'ARQUIVO': str}) 
            lista_dfs.append(df)
        except Exception as e:
            logger.warning(f"Falha ao ler o arquivo '{f.name}': {e}. Pulando.")
            continue
    
    if not lista_dfs:
        return pd.DataFrame()
        
    df_consolidado = pd.concat(lista_dfs, ignore_index=True)
    logger.info(f"Total de {len(df_consolidado)} itens consolidados de {len(lista_dfs)} arquivos.")
    return df_consolidado

def deve_manter(row: pd.Series) -> bool:
    """
    Função de filtro que decide se uma linha deve ser mantida no master.xlsx.
    Agora inclui logging para itens rejeitados.
    """
    desc = str(row.get('DESCRICAO', ''))
    ref = str(row.get('REFERENCIA', ''))
    texto_completo = f"{desc} {ref}"
    
    # Adiciona informações de contexto para o log
    item_info = f"Arquivo: {row.get('ARQUIVO', 'N/A')}, Item: {row.get('Nº', 'N/A')}"

    # 1. Verifica se é uma exceção que deve ser mantida
    if REGEX_EXCECAO.search(texto_completo):
        return True

    # 2. Verifica se contém uma palavra de exclusão
    match_excluir = REGEX_EXCLUIR.search(texto_completo)
    if match_excluir:
        # Se encontrou uma palavra para excluir, loga o motivo e retorna False
        palavra_excluida = match_excluir.group(0)
        logger.warning(f"ITEM REJEITADO | {item_info} | Palavra de exclusão encontrada: '{palavra_excluida}'")
        return False
        
    # 3. Se não foi excluído, mantém o item
    return True

# =====================================================================================
# 3. ORQUESTRADOR
# =====================================================================================

def main():
    """
    Orquestra o processo em duas fases:
    1. GERAÇÃO: Cria os arquivos '*_master.xlsx' individuais em cada subpasta.
    2. CONSOLIDAÇÃO: Junta todos, cria 'summary.xlsx' e 'master.xlsx' filtrado.
    """
    logger.info("="*80)
    logger.info("INICIANDO SCRIPT DE MERGE E CONSOLIDAÇÃO (05_joint_master.py)")
    logger.info("="*80)

    # --- FASE 1: Geração dos Masters Individuais ---
    logger.info("[FASE 1 de 2] Gerando arquivos master individuais por edital...")
    if not PASTA_EDITAIS.is_dir():
        logger.critical(f"Diretório base de editais '{PASTA_EDITAIS}' não existe. Encerrando.")
        return
        
    pastas_de_editais = [d for d in PASTA_EDITAIS.iterdir() if d.is_dir()]
    for pasta in pastas_de_editais:
        master_path = pasta / f"{pasta.name}{MASTER_SUFFIX}"
        if master_path.exists():
            logger.info(f"Arquivo '{master_path.name}' já existe em '{pasta.name}'. Pulando geração.")
            continue
        # Se o arquivo não existir, prossegue com a criação
        criar_master_individual(pasta)
    
    logger.info("[FASE 1 de 2] Concluída.")

    # --- FASE 2: Consolidação e Filtragem ---
    logger.info("\n[FASE 2 de 2] Consolidando e filtrando arquivos master...")
    arquivos_master = encontrar_arquivos_master(PASTA_EDITAIS)
    if not arquivos_master:
        logger.warning("Nenhum arquivo '*_master.xlsx' encontrado para consolidação. Encerrando.")
        return

    df_total = consolidar_dataframes(arquivos_master)
    if df_total.empty:
        logger.error("Nenhum dado foi consolidado. Não é possível gerar os arquivos finais.")
        return

    # Geração do Summary
    logger.info(f"Gerando '{SUMMARY_EXCEL_PATH.name}' com {len(df_total)} itens...")
    df_total.to_excel(SUMMARY_EXCEL_PATH, index=False)
    logger.info(f" > OK: Arquivo '{SUMMARY_EXCEL_PATH.name}' criado com sucesso.")

    # Geração do Master Final Filtrado
    logger.info(f"Iniciando filtragem para gerar '{FINAL_MASTER_PATH.name}'...")
    df_master = df_total.copy()
    df_master['DESCRICAO'] = df_master['DESCRICAO'].fillna('').astype(str)
    df_master['REFERENCIA'] = df_master['REFERENCIA'].fillna('').astype(str)

    mask_descricao = df_master['DESCRICAO'].str.contains(REGEX_FILTRO.pattern, regex=True, case=False, na=False)
    mask_referencia = df_master['REFERENCIA'].str.contains(REGEX_FILTRO.pattern, regex=True, case=False, na=False)
    df_relevantes = df_master[mask_descricao | mask_referencia]
    
    if not df_relevantes.empty:
        mask_final = df_relevantes.apply(deve_manter, axis=1)
        df_filtrado = df_relevantes[mask_final].copy()
    else:
        df_filtrado = pd.DataFrame(columns=df_relevantes.columns)

    if not df_filtrado.empty:
        df_filtrado.loc[:, 'TIMESTAMP'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"Gerando '{FINAL_MASTER_PATH.name}' com {len(df_filtrado)} itens filtrados...")
        df_filtrado.to_excel(FINAL_MASTER_PATH, index=False)
        logger.info(f" > OK: Arquivo '{FINAL_MASTER_PATH.name}' criado com sucesso.")
    else:
        logger.warning(" > AVISO: Nenhum item passou pelos filtros. O arquivo 'master.xlsx' será gerado em branco.")
        pd.DataFrame().to_excel(FINAL_MASTER_PATH, index=False)

    logger.info("[FASE 2 de 2] Concluída.")
    logger.info("="*80)
    logger.info("PROCESSO CONCLUÍDO!")
    logger.info("="*80)


if __name__ == "__main__":
    main()
