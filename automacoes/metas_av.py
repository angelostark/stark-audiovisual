#!/usr/bin/env python3
"""
=====================================================================
AUTOMAÇÃO DE METAS — TIME AUDIOVISUAL STARK
=====================================================================
Lê dados de planilhas-fonte, calcula KPIs e escreve na planilha de metas.

Uso:
  python3 automacoes/metas_av.py                  # Mês atual
  python3 automacoes/metas_av.py --mes 3 --ano 2026  # Mês específico
  python3 automacoes/metas_av.py --dry-run           # Só calcula, não escreve

Requer:
  pip install gspread google-auth
  Arquivo de credenciais: automacoes/credentials.json
=====================================================================
"""

import gspread
import json
import sys
import os
import re
import argparse
import unicodedata
from datetime import datetime
from google.oauth2.service_account import Credentials

# =====================================================================
# CONFIGURAÇÃO
# =====================================================================

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
]

# IDs das planilhas
METAS_SHEET_ID = '1iHnabzZ1LkIaihBSrx2HS6DXYju3juY0VHuvZvSIEjc'
METAS_GID = 386782566

LAYOUTS_SHEET_ID = '18IYDy4Pktx9f_86Jp-k6ErAXsFh7yKrPafcdhEvoa_o'
ENTREGAS_SHEET_ID = '1qdAeMWXRegtIL53n8cebwOwdQeF95BCvz7macrtN4DA'
REFACOES_SHEET_ID = '1avv5PapqdKdPc92Uqxm-SW7LL6lcgJ3_D8Wz1461ieM'
POSTS_SHEET_ID = '1fmOrGlXm6ZIdbu3rI2wpPTUtpNfluSM_XdJ8JyoTi0I'
VIDEOS_SHEET_ID = '10NyWM4CFJHyNFaveh48FGq7mfWrzOTWMwAH-rZEsJJY'

# Mapeamento de nomes (primeiro nome → nome completo nas fontes)
NOMES = {
    'Eloy':     'Eloy Lopes',
    'Wygor':    'Wygor Matheus',
    'Humberto': 'Humberto Salles',
    'Fábio':    'Fábio Silva',
    'Karyne':   'Karyne Torres',
    'Milena':   'Milena Carneiro',
    'João':     'João',
    'Max':      'Max',
    'André':    'Andre Mello',
    'Ebertty':  'Ebertty Matnai',
    'Mateus':   'Mateus Redmann',
}

MESES_PT = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

# E-mail para notificação (opcional)
EMAIL_NOTIFICACAO = 'angelo@starkmkt.com'


# =====================================================================
# UTILITÁRIOS DE NOME
# =====================================================================

def normalizar(texto):
    """Remove acentos e converte para uppercase para comparação."""
    texto = str(texto).strip()
    nfkd = unicodedata.normalize('NFKD', texto)
    sem_acento = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.upper()


def match_nome(celula_texto):
    """Tenta casar o texto da célula com um colaborador conhecido."""
    celula_norm = normalizar(celula_texto)
    if not celula_norm or len(celula_norm) < 2:
        return None

    # Ignorar textos que claramente não são nomes
    ignorar = ['SEMANA', 'NOME', 'TOTAL', 'POSTS', 'DESIGNER', 'EDITOR',
               'LAYOUT', 'CARROSSEL', 'ESTATICO', 'REELS', 'CAPA', 'MES',
               'PORCENTAGEM', 'ENTREGUES', 'SEREM']
    if celula_norm in ignorar:
        return None

    # Match exato por primeiro nome
    for primeiro_nome in NOMES:
        if normalizar(primeiro_nome) == celula_norm:
            return primeiro_nome

    # Match exato por nome completo
    for primeiro_nome, nome_completo in NOMES.items():
        if normalizar(nome_completo) == celula_norm:
            return primeiro_nome

    # Match parcial — primeiro nome contido na célula
    for primeiro_nome in NOMES:
        nome_norm = normalizar(primeiro_nome)
        if len(nome_norm) >= 3 and nome_norm in celula_norm and len(celula_norm) < 30:
            return primeiro_nome

    # Match parcial — nome completo contido na célula
    for primeiro_nome, nome_completo in NOMES.items():
        nome_norm = normalizar(nome_completo)
        if nome_norm in celula_norm:
            return primeiro_nome

    return None


# =====================================================================
# AUTENTICAÇÃO
# =====================================================================

def autenticar():
    """Autentica com Google Sheets via service account."""
    if not os.path.exists(CREDENTIALS_PATH):
        print(f'❌ Arquivo de credenciais não encontrado: {CREDENTIALS_PATH}')
        print('   Execute o setup primeiro. Veja: automacoes/SETUP-GOOGLE-API.md')
        sys.exit(1)

    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    print('✅ Autenticado com Google Sheets API')
    return client


# =====================================================================
# BUSCAR ABA POR MÊS
# =====================================================================

def encontrar_aba(spreadsheet, mes, ano):
    """Encontra aba pelo nome do mês. Tenta várias variações."""
    mes_upper = mes.upper()
    mes_abrev = mes[:3].upper()
    mes_num = str(MESES_PT.index(mes) + 1).zfill(2)
    mes_norm = normalizar(mes)

    padroes = [
        mes, f'{mes} {ano}',
        mes_upper, f'{mes_upper} {ano}',
        mes_abrev, f'{mes_abrev} {ano}',
        f'{mes_num}/{ano}', f'{mes_num}-{ano}',
        mes.lower(), f'{mes.lower()} {ano}',
    ]

    abas = spreadsheet.worksheets()

    # Busca exata
    for padrao in padroes:
        for aba in abas:
            if aba.title.strip().upper() == padrao.upper():
                return aba

    # Busca normalizada (sem acentos)
    for aba in abas:
        titulo_norm = normalizar(aba.title)
        if titulo_norm == mes_norm or titulo_norm == f'{mes_norm} {ano}':
            return aba

    # Busca parcial (contém o nome do mês)
    for aba in abas:
        titulo_norm = normalizar(aba.title)
        if mes_norm in titulo_norm or mes_abrev in titulo_norm:
            return aba

    return None


# =====================================================================
# PROCESSAR LAYOUTS (DINÂMICO)
# =====================================================================

def processar_layouts(client, mes, ano):
    """
    Lê planilha de Layouts e verifica 20/20 preenchidos.
    Detecta DINAMICAMENTE quais designers estão na aba do mês.
    Retorna: { 'Eloy': 1.0, 'João': 0.0, ... }
    """
    print('\n📐 NOVOS MODELOS DE LAYOUT')
    print('─' * 40)

    resultado = {}

    try:
        ss = client.open_by_key(LAYOUTS_SHEET_ID)
    except Exception as e:
        print(f'  ⚠️ Erro ao abrir planilha de Layouts: {e}')
        return resultado

    aba = encontrar_aba(ss, mes, ano)
    if not aba:
        print(f'  ⚠️ Aba de {mes} {ano} não encontrada.')
        return resultado

    print(f'  Aba: "{aba.title}"')
    dados = aba.get_all_values()

    # Encontrar linha de header — procurar linha com 2+ nomes de colaboradores
    header_row = -1
    colunas_por_designer = {}

    for i, row in enumerate(dados[:15]):
        matches_na_linha = {}
        for j, celula in enumerate(row):
            nome_match = match_nome(celula)
            if nome_match and nome_match not in matches_na_linha:
                matches_na_linha[nome_match] = j

        if len(matches_na_linha) >= 2:
            header_row = i
            colunas_por_designer = matches_na_linha
            break

    if header_row == -1:
        print('  ⚠️ Headers com nomes de designers não encontrados.')
        return resultado

    designers_encontrados = list(colunas_por_designer.keys())
    print(f'  Designers neste mês: {", ".join(designers_encontrados)}')

    # Verificar slots 1-20 após header
    # Conta linhas de dados: tem número na col 0 OU tem conteúdo em qualquer coluna de designer
    linhas_dados = []
    for i in range(header_row + 1, min(header_row + 30, len(dados))):
        row = dados[i]
        num_col = str(row[0]).strip() if row else ''
        # É linha de dados se tem número 1-20 ou se a maioria dos designers tem conteúdo
        is_numbered = False
        try:
            num = int(num_col)
            if 1 <= num <= 20:
                is_numbered = True
        except ValueError:
            pass

        if not is_numbered:
            # Verificar se pelo menos metade das colunas de designers tem conteúdo
            cols_com_conteudo = 0
            for col_idx in colunas_por_designer.values():
                val = str(row[col_idx] if col_idx < len(row) else '').strip()
                if val:
                    cols_com_conteudo += 1
            if cols_com_conteudo < len(colunas_por_designer) / 2:
                continue

        linhas_dados.append(i)
        if len(linhas_dados) >= 20:
            break

    for nome, col_idx in colunas_por_designer.items():
        preenchidos = 0
        for i in linhas_dados:
            row = dados[i]
            valor = str(row[col_idx] if col_idx < len(row) else '').strip()
            if valor and valor != '-' and valor != '0' and valor.lower() != 'undefined':
                preenchidos += 1

        resultado[nome] = 1.0 if preenchidos >= 20 else 0.0
        status = '100%' if resultado[nome] == 1.0 else '0%'
        print(f'  {nome}: {preenchidos}/20 → {status}')

    return resultado


# =====================================================================
# PROCESSAR VÍDEOS (EDITORES — COLUNA F)
# =====================================================================

def processar_videos(client, mes, ano):
    """
    Lê planilha 'Vídeos Novos' e verifica 50% preenchidos (10/20).
    Estrutura: header com nomes de editores, 20 slots numerados.
    Se preencheu >= 50% → 100%, senão → 0%.
    Retorna: { 'André': 1.0, 'Ebertty': 0.0, ... }
    """
    print('\n🎬 NOVOS MODELOS DE VÍDEO')
    print('─' * 40)

    resultado = {}

    try:
        ss = client.open_by_key(VIDEOS_SHEET_ID)
    except Exception as e:
        print(f'  ⚠️ Erro ao abrir planilha de Vídeos: {e}')
        return resultado

    aba = encontrar_aba(ss, mes, ano)
    if not aba:
        print(f'  ⚠️ Aba de {mes} {ano} não encontrada.')
        return resultado

    print(f'  Aba: "{aba.title}"')
    dados = aba.get_all_values()

    # Encontrar header com nomes de editores
    header_row = -1
    colunas_por_editor = {}

    for i, row in enumerate(dados[:15]):
        matches_na_linha = {}
        for j, celula in enumerate(row):
            nome_match = match_nome(celula)
            if nome_match and nome_match not in matches_na_linha:
                matches_na_linha[nome_match] = j

        if len(matches_na_linha) >= 2:
            header_row = i
            colunas_por_editor = matches_na_linha
            break

    if header_row == -1:
        print('  ⚠️ Headers com nomes de editores não encontrados.')
        return resultado

    editores_encontrados = list(colunas_por_editor.keys())
    print(f'  Editores neste mês: {", ".join(editores_encontrados)}')

    # Contar slots preenchidos (linhas numeradas 1-20 após header)
    linhas_dados = []
    for i in range(header_row + 1, min(header_row + 30, len(dados))):
        row = dados[i]
        num_col = str(row[0]).strip() if row else ''
        try:
            num = int(num_col)
            if 1 <= num <= 20:
                linhas_dados.append(i)
        except ValueError:
            pass
        if len(linhas_dados) >= 20:
            break

    total_slots = len(linhas_dados)
    threshold = total_slots * 0.5

    for nome, col_idx in colunas_por_editor.items():
        preenchidos = 0
        for i in linhas_dados:
            row = dados[i]
            valor = str(row[col_idx] if col_idx < len(row) else '').strip()
            if valor and valor != '-' and valor != '0' and valor.lower() != 'undefined':
                preenchidos += 1

        resultado[nome] = 1.0 if preenchidos >= threshold else 0.0
        status = '100%' if resultado[nome] == 1.0 else '0%'
        print(f'  {nome}: {preenchidos}/{total_slots} (mínimo {int(threshold)}) → {status}')

    return resultado


# =====================================================================
# PROCESSAR REFAÇÕES (COLUNA E)
# =====================================================================

def processar_refacoes(client, mes, ano):
    """
    Lê planilha 'Meta de Refações' e conta total de refações por pessoa no mês.
    Aba única 'refacoes'. Filtra por data (col 0) no mês/ano alvo.
    Retorna: { 'Eloy': 15, 'Fábio': 28, ... }
    """
    print('\n🔄 REFAÇÕES POR COLABORADOR')
    print('─' * 40)

    resultado = {}
    mes_idx = MESES_PT.index(mes) + 1

    try:
        ss = client.open_by_key(REFACOES_SHEET_ID)
    except Exception as e:
        print(f'  ⚠️ Erro ao abrir planilha de Refações: {e}')
        return resultado

    aba = ss.worksheet('refacoes')
    dados = aba.get_all_values()
    print(f'  Aba: "{aba.title}" ({len(dados) - 1} registros)')

    for row in dados[1:]:
        data_str = str(row[0]).strip() if row else ''
        if not data_no_mes(data_str, mes_idx, ano):
            continue

        nome_str = str(row[3]).strip() if len(row) > 3 else ''
        nome_encontrado = match_nome(nome_str)
        if not nome_encontrado:
            continue

        resultado[nome_encontrado] = resultado.get(nome_encontrado, 0) + 1

    for nome, count in sorted(resultado.items(), key=lambda x: -x[1]):
        print(f'  {nome}: {count} refações')

    # Preencher ausentes com 0
    for nome in NOMES:
        if nome not in resultado:
            resultado[nome] = 0
            print(f'  {nome}: 0 refações')

    return resultado


# =====================================================================
# PROCESSAR POSTS CRIADOS (COLUNA E — DENOMINADOR)
# =====================================================================

def processar_posts_criados(client, mes, ano):
    """
    Lê planilha 'Dados - Posts criados' e soma total de posts por pessoa no mês.
    Designers: soma col 'Total' (idx 5) das linhas semanais do lado esquerdo.
    Editores: lê totais individuais do resumo no lado direito.
    Retorna: { 'Eloy': 138, 'André': 131, ... }
    """
    print('\n📊 POSTS CRIADOS POR COLABORADOR')
    print('─' * 40)

    resultado = {}

    try:
        ss = client.open_by_key(POSTS_SHEET_ID)
    except Exception as e:
        print(f'  ⚠️ Erro ao abrir planilha de Posts Criados: {e}')
        return resultado

    aba = encontrar_aba(ss, mes, ano)
    if not aba:
        print(f'  ⚠️ Aba de {mes} {ano} não encontrada.')
        return resultado

    print(f'  Aba: "{aba.title}"')
    dados = aba.get_all_values()

    # Designers: somar col Total (idx 5) por nome (col 1) das linhas semanais
    for row in dados[1:]:
        nome_str = str(row[1]).strip() if len(row) > 1 else ''
        total_str = str(row[5]).strip() if len(row) > 5 else ''

        nome_encontrado = match_nome(nome_str)
        if not nome_encontrado:
            continue

        try:
            total = int(total_str) if total_str else 0
        except ValueError:
            continue

        resultado[nome_encontrado] = resultado.get(nome_encontrado, 0) + total

    # Editores: buscar no lado direito (resumo)
    # Estrutura: linha com nomes de editores (col 7+), linha seguinte com totais
    for i, row in enumerate(dados):
        # Procurar linha com nomes de editores no lado direito
        nomes_editores_encontrados = {}
        for j in range(7, min(len(row), 13)):
            nome_match = match_nome(str(row[j]).strip())
            if nome_match and nome_match in ['André', 'Ebertty', 'Mateus']:
                nomes_editores_encontrados[j] = nome_match

        if len(nomes_editores_encontrados) >= 2 and i + 1 < len(dados):
            # Linha seguinte tem os totais
            totais_row = dados[i + 1]
            for col_idx, nome in nomes_editores_encontrados.items():
                if nome in resultado:
                    continue  # Já foi preenchido
                val_str = str(totais_row[col_idx]).strip() if col_idx < len(totais_row) else ''
                try:
                    resultado[nome] = int(val_str) if val_str else 0
                except ValueError:
                    resultado[nome] = 0

    for nome in sorted(resultado, key=lambda n: -resultado.get(n, 0)):
        print(f'  {nome}: {resultado[nome]} posts')

    # Preencher ausentes com 0
    for nome in NOMES:
        if nome not in resultado:
            resultado[nome] = 0
            print(f'  {nome}: 0 posts')

    return resultado


def calcular_alteracoes(dados_refacoes, dados_posts):
    """
    Calcula % de posts SEM alterações: 1 - (refações / posts criados).
    Quanto maior, melhor (menos refações = mais qualidade).
    Retorna: { 'Eloy': 0.7101, 'Fábio': 0.5658, ... }
    """
    resultado = {}
    for nome in NOMES:
        refacoes = dados_refacoes.get(nome, 0)
        posts = dados_posts.get(nome, 0)
        if posts > 0:
            resultado[nome] = 1.0 - (refacoes / posts)
        else:
            resultado[nome] = 0.0
    return resultado


# =====================================================================
# PROCESSAR ENTREGAS (COM MATCHING FLEXÍVEL)
# =====================================================================

def parse_percentual(texto):
    """Converte texto de percentual ('100,00%', '88,00%') para float (1.0, 0.88)."""
    if not texto or not isinstance(texto, str):
        return None
    texto = texto.strip()
    if texto.startswith('#') or texto == '':
        return None
    valor_limpo = texto.replace(',', '.').replace('%', '').strip()
    try:
        num = float(valor_limpo)
        if 0 <= num <= 1.5:
            return num
        elif 0 < num <= 150:
            return num / 100
    except ValueError:
        pass
    return None


def data_no_mes(data_str, mes_idx, ano):
    """Verifica se uma data (dd/mm/yyyy) pertence ao mês/ano alvo."""
    data_str = str(data_str).strip()
    if not data_str:
        return False
    try:
        partes = data_str.split('/')
        if len(partes) == 3:
            d, m, a = int(partes[0]), int(partes[1]), int(partes[2])
            return m == mes_idx and a == ano
    except (ValueError, IndexError):
        pass
    return False


def processar_entregas(client, mes, ano):
    """
    Lê planilha de Entregas e calcula média % por pessoa.
    Estrutura: 2 seções lado a lado (Designers cols 0-4, Editores cols 6-10).
    Cada seção: Semana | Nome | Posts a Serem | Posts Entregues | Porcentagem
    Filtra apenas linhas do mês/ano alvo.
    Retorna: { 'Eloy': 0.88, 'André': 0.95, ... }
    """
    print('\n📦 PRAZO DE ENTREGA DE DEMANDAS')
    print('─' * 40)

    resultado = {}
    mes_idx = MESES_PT.index(mes) + 1

    try:
        ss = client.open_by_key(ENTREGAS_SHEET_ID)
    except Exception as e:
        print(f'  ⚠️ Erro ao abrir planilha de Entregas: {e}')
        for nome in NOMES:
            resultado[nome] = 0.0
        return resultado

    aba = encontrar_aba(ss, mes, ano)
    if not aba:
        print(f'  ⚠️ Aba de {mes} {ano} não encontrada. Usando 0% para todos.')
        for nome in NOMES:
            resultado[nome] = 0.0
        return resultado

    print(f'  Aba: "{aba.title}"')
    dados = aba.get_all_values()

    if not dados:
        for nome in NOMES:
            resultado[nome] = 0.0
        return resultado

    # Detectar seções pelo header (linha 0)
    # Seção 1 (Designers): cols 0-4 → nome col 1, a_serem col 2, entregues col 3
    # Seção 2 (Editores):  cols 6-10 → nome col 7, a_serem col 8, entregues col 9
    secoes = [
        {'col_data': 0, 'col_nome': 1, 'col_serem': 2, 'col_entregues': 3},
        {'col_data': 6, 'col_nome': 7, 'col_serem': 8, 'col_entregues': 9},
    ]

    totais_por_pessoa = {}  # {nome: {'serem': int, 'entregues': int}}

    for row in dados[1:]:  # Pular header
        for secao in secoes:
            col_data = secao['col_data']
            col_nome = secao['col_nome']
            col_serem = secao['col_serem']
            col_entregues = secao['col_entregues']

            if col_nome >= len(row):
                continue

            data_str = str(row[col_data]).strip() if col_data < len(row) else ''
            nome_str = str(row[col_nome]).strip() if col_nome < len(row) else ''

            # Filtrar por mês
            if not data_no_mes(data_str, mes_idx, ano):
                continue

            nome_encontrado = match_nome(nome_str)
            if not nome_encontrado:
                continue

            # Ler valores numéricos de posts
            serem_str = str(row[col_serem]).strip() if col_serem < len(row) else ''
            entreg_str = str(row[col_entregues]).strip() if col_entregues < len(row) else ''

            try:
                serem = int(serem_str) if serem_str else 0
                entregues = int(entreg_str) if entreg_str else 0
            except ValueError:
                continue

            if serem <= 0:
                continue

            if nome_encontrado not in totais_por_pessoa:
                totais_por_pessoa[nome_encontrado] = {'serem': 0, 'entregues': 0, 'semanas': 0}
            totais_por_pessoa[nome_encontrado]['serem'] += serem
            totais_por_pessoa[nome_encontrado]['entregues'] += entregues
            totais_por_pessoa[nome_encontrado]['semanas'] += 1

    # Calcular total entregues / total a serem
    for nome, totais in totais_por_pessoa.items():
        if totais['serem'] > 0:
            media = totais['entregues'] / totais['serem']
            resultado[nome] = media
            print(f'  {nome}: {totais["semanas"]} semanas → {totais["entregues"]}/{totais["serem"]} = {media * 100:.2f}%')

    # Preencher ausentes com 0
    for nome in NOMES:
        if nome not in resultado:
            resultado[nome] = 0.0
            print(f'  {nome}: não encontrado → 0%')

    return resultado


# =====================================================================
# ESCREVER NA PLANILHA DE METAS
# =====================================================================

def escrever_metas(client, dados_layouts, dados_entregas, dados_alteracoes, dados_videos, mes, ano, dry_run=False):
    """Escreve os valores calculados na planilha de Metas."""
    print('\n📝 ESCREVENDO NA PLANILHA DE METAS')
    print('─' * 40)

    ss = client.open_by_key(METAS_SHEET_ID)

    # Encontrar aba pelo nome do mês
    aba_metas = encontrar_aba(ss, mes, ano)

    if not aba_metas:
        # Aba do mês não existe → duplicar a mais recente
        print(f'  ⚠️ Aba "{mes}" não encontrada. Criando a partir da aba anterior...')
        abas = ss.worksheets()
        # Encontrar a aba do mês anterior como modelo
        mes_idx = MESES_PT.index(mes)
        aba_modelo = None
        # Tentar mês anterior, depois qualquer mês existente
        for offset in range(1, 13):
            idx_anterior = (mes_idx - offset) % 12
            nome_anterior = MESES_PT[idx_anterior]
            for aba in abas:
                if normalizar(aba.title) == normalizar(nome_anterior):
                    aba_modelo = aba
                    break
            if aba_modelo:
                break

        if not aba_modelo:
            print(f'  ❌ Nenhuma aba modelo encontrada para duplicar!')
            return False

        if dry_run:
            print(f'  🔍 DRY RUN: criaria aba "{mes}" copiando de "{aba_modelo.title}"')
            # Para dry-run, usar a aba modelo para mostrar o que seria escrito
            aba_metas = aba_modelo
        else:
            new_sheet = ss.duplicate_sheet(aba_modelo.id, new_sheet_name=mes)
            aba_metas = ss.worksheet(mes)
            print(f'  ✅ Aba "{mes}" criada!')

    print(f'  Aba: "{aba_metas.title}"')
    dados = aba_metas.get_all_values()

    # Encontrar headers — pode haver 2 seções (designers linha 0, editores linha 11+)
    secoes_headers = []

    for i, row in enumerate(dados):
        col_nome = -1
        col_layout = -1
        col_prazo = -1
        col_alteracoes = -1

        for j, celula in enumerate(row):
            celula_lower = str(celula).strip().lower()
            if 'nome' in celula_lower and 'prestador' in celula_lower:
                col_nome = j
            if 'novos modelos' in celula_lower or ('layout' in celula_lower and 'novos' in celula_lower) or ('novos modelos' in celula_lower and 'vídeo' in celula_lower) or ('novos modelos' in celula_lower and 'video' in celula_lower):
                col_layout = j
            if 'prazo' in celula_lower and 'entrega' in celula_lower:
                col_prazo = j
            if 'alteraç' in celula_lower and 'responsabilidade' in celula_lower:
                col_alteracoes = j

        if col_nome != -1:
            secoes_headers.append({
                'header_row': i,
                'col_nome': col_nome,
                'col_layout': col_layout,
                'col_prazo': col_prazo,
                'col_alteracoes': col_alteracoes,
            })

    if not secoes_headers:
        print('  ❌ Headers não encontrados na planilha de Metas!')
        return False

    for sec in secoes_headers:
        cols_info = f'Nome(col {sec["col_nome"]+1})'
        if sec['col_alteracoes'] != -1:
            cols_info += f', Alterações(col {sec["col_alteracoes"]+1})'
        if sec['col_layout'] != -1:
            cols_info += f', Layout/Vídeo(col {sec["col_layout"]+1})'
        if sec['col_prazo'] != -1:
            cols_info += f', Prazo(col {sec["col_prazo"]+1})'
        print(f'  Seção linha {sec["header_row"] + 1}: {cols_info}')

    if dry_run:
        print('\n  🔍 DRY RUN — valores que seriam escritos:')

    # Coletar atualizações em batch
    atualizacoes = []
    preenchidos = 0

    for sec in secoes_headers:
        header_row = sec['header_row']
        col_nome = sec['col_nome']
        col_layout = sec['col_layout']
        col_prazo = sec['col_prazo']
        col_alteracoes = sec['col_alteracoes']

        # Determinar fim da seção (próximo header ou fim dos dados)
        next_headers = [s['header_row'] for s in secoes_headers if s['header_row'] > header_row]
        fim_secao = min(next_headers) if next_headers else len(dados)

        for i in range(header_row + 1, fim_secao):
            nome_celula = str(dados[i][col_nome] if col_nome < len(dados[i]) else '').strip()
            if not nome_celula:
                continue

            primeiro_nome = match_nome(nome_celula)
            if not primeiro_nome:
                continue

            # Alterações por Responsabilidade (col E)
            if col_alteracoes != -1:
                valor_alt = dados_alteracoes.get(primeiro_nome, 0.0)
                cell_alt = gspread.utils.rowcol_to_a1(i + 1, col_alteracoes + 1)
                atualizacoes.append({
                    'range': cell_alt,
                    'values': [[valor_alt]]
                })
                if dry_run:
                    print(f'    {primeiro_nome}: Alterações = {valor_alt * 100:.2f}%')

            # Layout/Vídeo — designers usam dados_layouts, editores usam dados_videos
            if col_layout != -1:
                if primeiro_nome in dados_layouts:
                    valor_layout = dados_layouts[primeiro_nome]
                elif primeiro_nome in dados_videos:
                    valor_layout = dados_videos[primeiro_nome]
                else:
                    valor_layout = None

                if valor_layout is not None:
                    cell_layout = gspread.utils.rowcol_to_a1(i + 1, col_layout + 1)
                    atualizacoes.append({
                        'range': cell_layout,
                        'values': [[valor_layout]]
                    })
                    if dry_run:
                        print(f'    {primeiro_nome}: Layout = {valor_layout * 100:.0f}%')
                elif dry_run:
                    print(f'    {primeiro_nome}: Layout = (não participa neste mês, mantém atual)')

            # Prazo
            if col_prazo != -1:
                valor_prazo = dados_entregas.get(primeiro_nome, 0.0)
                cell_prazo = gspread.utils.rowcol_to_a1(i + 1, col_prazo + 1)
                atualizacoes.append({
                    'range': cell_prazo,
                    'values': [[valor_prazo]]
                })
                if dry_run:
                    print(f'    {primeiro_nome}: Prazo = {valor_prazo * 100:.2f}%')

            preenchidos += 1

    if dry_run:
        print(f'\n  Total: {preenchidos} colaboradores (simulação)')
        return True

    # Escrever em batch
    if atualizacoes:
        aba_metas.batch_update(atualizacoes, value_input_option='USER_ENTERED')
        print(f'  ✅ {preenchidos} colaboradores atualizados ({len(atualizacoes)} células)')
    else:
        print('  ⚠️ Nenhuma atualização a fazer.')

    return True


# =====================================================================
# RESUMO
# =====================================================================

def imprimir_resumo(dados_layouts, dados_entregas, dados_alteracoes, dados_videos):
    """Imprime resumo formatado dos resultados."""
    print('\n' + '=' * 50)
    print('📊 RESUMO DAS METAS')
    print('=' * 50)

    todos_nomes = list(NOMES.keys())
    designers = [n for n in todos_nomes if n not in ['André', 'Ebertty', 'Mateus']]
    editores = ['André', 'Ebertty', 'Mateus']

    print(f'\n{"Nome":<12} {"Alterações":>12} {"Layout/Vídeo":>13} {"Prazo":>10}')
    print('─' * 49)

    print('DESIGNERS:')
    for nome in designers:
        alt = dados_alteracoes.get(nome, 0.0)
        layout = dados_layouts.get(nome, None)
        prazo = dados_entregas.get(nome, 0.0)
        alt_str = f'{alt * 100:.2f}%'
        layout_str = f'{layout * 100:.0f}%' if layout is not None else 'N/A'
        prazo_str = f'{prazo * 100:.2f}%'
        print(f'  {nome:<10} {alt_str:>12} {layout_str:>13} {prazo_str:>10}')

    print('\nEDITORES:')
    for nome in editores:
        alt = dados_alteracoes.get(nome, 0.0)
        video = dados_videos.get(nome, None)
        prazo = dados_entregas.get(nome, 0.0)
        alt_str = f'{alt * 100:.2f}%'
        video_str = f'{video * 100:.0f}%' if video is not None else 'N/A'
        prazo_str = f'{prazo * 100:.2f}%'
        print(f'  {nome:<10} {alt_str:>12} {video_str:>13} {prazo_str:>10}')


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description='Automação de Metas AV — Stark')
    parser.add_argument('--mes', type=int, help='Mês (1-12). Default: mês atual')
    parser.add_argument('--ano', type=int, help='Ano. Default: ano atual')
    parser.add_argument('--mes-anterior', action='store_true',
                        help='Processa o mês anterior ao atual (ex: roda em abril → processa março)')
    parser.add_argument('--dry-run', action='store_true', help='Só calcula, não escreve')
    args = parser.parse_args()

    hoje = datetime.now()

    if args.mes_anterior:
        # Mês anterior: se janeiro, volta para dezembro do ano anterior
        if hoje.month == 1:
            mes_idx = 11  # Dezembro (0-indexed)
            ano = hoje.year - 1
        else:
            mes_idx = hoje.month - 2  # -2 porque é 0-indexed
            ano = hoje.year
    else:
        mes_idx = (args.mes or hoje.month) - 1
        ano = args.ano or hoje.year

    mes = MESES_PT[mes_idx]

    print('=' * 50)
    print(f'🎯 AUTOMAÇÃO DE METAS — {mes.upper()} {ano}')
    print('=' * 50)

    # Autenticar
    client = autenticar()

    # Processar fontes
    dados_layouts = processar_layouts(client, mes, ano)
    dados_videos = processar_videos(client, mes, ano)
    dados_entregas = processar_entregas(client, mes, ano)
    dados_refacoes = processar_refacoes(client, mes, ano)
    dados_posts = processar_posts_criados(client, mes, ano)
    dados_alteracoes = calcular_alteracoes(dados_refacoes, dados_posts)

    # Resumo
    imprimir_resumo(dados_layouts, dados_entregas, dados_alteracoes, dados_videos)

    # Escrever
    if args.dry_run:
        escrever_metas(client, dados_layouts, dados_entregas, dados_alteracoes, dados_videos, mes, ano, dry_run=True)
        print('\n🔍 Modo DRY RUN — nada foi escrito na planilha.')
    else:
        sucesso = escrever_metas(client, dados_layouts, dados_entregas, dados_alteracoes, dados_videos, mes, ano)
        if sucesso:
            print('\n✅ Metas atualizadas com sucesso!')
        else:
            print('\n❌ Falha ao atualizar metas.')
            sys.exit(1)


if __name__ == '__main__':
    main()
