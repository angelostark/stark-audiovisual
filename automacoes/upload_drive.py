#!/usr/bin/env python3
"""
=====================================================================
UPLOAD PARA GOOGLE DRIVE — FLUXO FIGMA → DRIVE
=====================================================================
Navega a hierarquia de pastas do cliente no Drive (suporta Shared Drives),
cria subpasta da data se necessario e faz upload dos PNGs exportados do Figma.

Uso:
  python3 automacoes/upload_drive.py \
    --client "Stark" \
    --date "2026-03-17" \
    --files /tmp/figma_exports/2026-03-17-Stark-card-01.png \
            /tmp/figma_exports/2026-03-17-Stark-card-02.png

  # Dry run (testa navegacao sem upload):
  python3 automacoes/upload_drive.py \
    --client "Stark" \
    --date "2026-03-17" \
    --dry-run

Requer:
  pip install google-api-python-client google-auth
  Arquivo de credenciais: automacoes/credentials.json
  Drive Compartilhado "Clientes" acessivel pelo service account

Retorna JSON:
  {
    "folder_id": "...",
    "folder_link": "https://drive.google.com/drive/folders/...",
    "files": [{"name": "card-01.png", "id": "...", "link": "..."}]
  }
=====================================================================
"""

import argparse
import json
import os
import sys
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =====================================================================
# CONFIGURACAO
# =====================================================================

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')

SCOPES = [
    'https://www.googleapis.com/auth/drive',
]

# Nomes alternativos para pasta de conteudo (ordem de prioridade)
CONTENT_FOLDER_NAMES = [
    'Cronograma de Conteúdo',
    'C. Conteúdo',
    'Cronograma de Conteudo',
    'C. Conteudo',
]

# Mapa de numero do mes para nome em portugues
MESES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}


# =====================================================================
# FUNCOES AUXILIARES
# =====================================================================

def get_drive_service():
    """Autentica e retorna o servico do Google Drive."""
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"ERRO: Arquivo de credenciais nao encontrado: {CREDENTIALS_PATH}", file=sys.stderr)
        print("Execute o setup: automacoes/SETUP-GOOGLE-API.md", file=sys.stderr)
        sys.exit(1)

    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)


def find_shared_drive(service, name):
    """Busca um Shared Drive (Drive Compartilhado) pelo nome."""
    results = service.drives().list(
        pageSize=50,
    ).execute()

    drives = results.get('drives', [])
    for d in drives:
        if d['name'].strip().lower() == name.strip().lower():
            return d
    return None


def find_folder(service, name, parent_id, drive_id=None):
    """Busca uma pasta pelo nome dentro de um parent. Suporta Shared Drives."""
    safe_name = name.replace("'", "\\'")
    query = f"name = '{safe_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    query += f" and '{parent_id}' in parents"

    kwargs = {
        'q': query,
        'fields': 'files(id, name, webViewLink)',
        'pageSize': 5,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
    }
    if drive_id:
        kwargs['driveId'] = drive_id
        kwargs['corpora'] = 'drive'

    results = service.files().list(**kwargs).execute()
    files = results.get('files', [])
    return files[0] if files else None


def find_folder_contains(service, search_text, parent_id, drive_id=None):
    """Busca uma pasta cujo nome CONTEM o texto (busca parcial). Suporta Shared Drives.
    Util para pastas com prefixo/sufixo como '03. Cronograma de Conteúdo | Oi'."""
    safe_text = search_text.replace("'", "\\'")
    query = f"name contains '{safe_text}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    query += f" and '{parent_id}' in parents"

    kwargs = {
        'q': query,
        'fields': 'files(id, name, webViewLink)',
        'pageSize': 10,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
    }
    if drive_id:
        kwargs['driveId'] = drive_id
        kwargs['corpora'] = 'drive'

    results = service.files().list(**kwargs).execute()
    files = results.get('files', [])
    return files[0] if files else None


def find_content_folder(service, parent_id, drive_id=None):
    """Busca a pasta de conteudo tentando match exato e parcial."""
    # Primeiro: match exato
    for name in CONTENT_FOLDER_NAMES:
        folder = find_folder(service, name, parent_id, drive_id)
        if folder:
            return folder
    # Segundo: match parcial (ex: "03. Cronograma de Conteúdo | Cliente")
    for name in CONTENT_FOLDER_NAMES:
        folder = find_folder_contains(service, name, parent_id, drive_id)
        if folder:
            return folder
    return None


def create_folder(service, name, parent_id):
    """Cria uma pasta dentro do parent especificado. Suporta Shared Drives."""
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id],
    }
    folder = service.files().create(
        body=metadata,
        fields='id, name, webViewLink',
        supportsAllDrives=True,
    ).execute()
    return folder


def upload_file(service, file_path, parent_id):
    """Faz upload de um arquivo para a pasta especificada. Suporta Shared Drives."""
    file_name = os.path.basename(file_path)

    # Detectar mimetype
    if file_name.lower().endswith('.png'):
        mimetype = 'image/png'
    elif file_name.lower().endswith('.jpg') or file_name.lower().endswith('.jpeg'):
        mimetype = 'image/jpeg'
    else:
        mimetype = 'application/octet-stream'

    metadata = {
        'name': file_name,
        'parents': [parent_id],
    }
    media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)

    uploaded = service.files().create(
        body=metadata,
        media_body=media,
        fields='id, name, webViewLink',
        supportsAllDrives=True,
    ).execute()

    return uploaded


def navigate_to_date_folder(service, client_name, date_str):
    """
    Navega a hierarquia completa ate a pasta da data:
    [Shared Drive Clientes] > [client] > Cronograma de Conteudo > Artes > [ano] > [mes] > [data]

    Suporta tanto Shared Drives quanto pastas regulares no My Drive.
    Retorna (folder_id, folder_link, created).
    """
    # Parse da data
    parts = date_str.split('-')
    if len(parts) != 3:
        print(f"ERRO: Data invalida '{date_str}'. Use formato YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)

    ano = parts[0]
    mes_num = int(parts[1])
    mes_nome = MESES.get(mes_num)
    if not mes_nome:
        print(f"ERRO: Mes invalido '{parts[1]}'.", file=sys.stderr)
        sys.exit(1)

    # Nivel 1: Tentar como Shared Drive primeiro, depois como pasta regular
    drive_id = None
    shared_drive = find_shared_drive(service, 'Clientes')

    if shared_drive:
        clientes_id = shared_drive['id']
        drive_id = shared_drive['id']
        print(f"  [1/7] Clientes (Shared Drive) → {clientes_id}")
    else:
        # Fallback: buscar como pasta no My Drive
        query = "name = 'Clientes' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(
            q=query,
            fields='files(id, name)',
            pageSize=5,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        files = results.get('files', [])
        if not files:
            print("ERRO: Pasta/Drive 'Clientes' nao encontrado.", file=sys.stderr)
            print("Verifique se foi compartilhado com o service account.", file=sys.stderr)
            sys.exit(1)
        clientes_id = files[0]['id']
        print(f"  [1/7] Clientes (pasta) → {clientes_id}")

    # Nivel 2: Cliente (match exato primeiro, depois parcial)
    cliente = find_folder(service, client_name, clientes_id, drive_id)
    if not cliente:
        # Tenta busca parcial (ex: "Fernando Bezerra" encontra "Dr. Fernando Bezerra")
        cliente = find_folder_contains(service, client_name, clientes_id, drive_id)
    if not cliente:
        print(f"ERRO: Pasta do cliente '{client_name}' nao encontrada dentro de 'Clientes'.", file=sys.stderr)
        sys.exit(1)
    print(f"  [2/7] {cliente['name']} → {cliente['id']}")

    # Nivel 3: Cronograma de Conteudo (com variacoes)
    conteudo = find_content_folder(service, cliente['id'], drive_id)
    if not conteudo:
        names = ' / '.join(CONTENT_FOLDER_NAMES)
        print(f"ERRO: Pasta de conteudo nao encontrada ({names}).", file=sys.stderr)
        sys.exit(1)
    print(f"  [3/7] {conteudo['name']} → {conteudo['id']}")

    # Nivel 4-5: Artes (opcional) + Ano
    # Primeiro, verifica se o ano ja existe direto dentro de Conteudo
    pasta_ano = find_folder(service, ano, conteudo['id'], drive_id)
    if pasta_ano:
        # Ano existe direto no Conteudo — pula "Artes"
        print(f"  [4/7] Artes — pulado (ano encontrado direto no Conteudo)")
        print(f"  [5/7] {ano} → {pasta_ano['id']}")
    else:
        # Ano nao existe direto — busca ou cria "Artes" e depois o ano
        # Tenta match exato "Artes", depois parcial (ex: "Artes | Dr. Fernando Bezerra")
        artes = find_folder(service, 'Artes', conteudo['id'], drive_id)
        if not artes:
            artes = find_folder_contains(service, 'Artes', conteudo['id'], drive_id)
        if not artes:
            artes = find_folder_contains(service, 'ARTES', conteudo['id'], drive_id)
        if not artes:
            print(f"  [4/7] Pasta 'Artes' nao existe — criando...")
            artes = create_folder(service, 'Artes', conteudo['id'])
        print(f"  [4/7] Artes → {artes['id']}")

        pasta_ano = find_folder(service, ano, artes['id'], drive_id)
        if not pasta_ano:
            print(f"  [5/7] Pasta '{ano}' nao existe — criando...")
            pasta_ano = create_folder(service, ano, artes['id'])
        print(f"  [5/7] {ano} → {pasta_ano['id']}")

    # Nivel 6: Mes
    pasta_mes = find_folder(service, mes_nome, pasta_ano['id'], drive_id)
    if not pasta_mes:
        print(f"  [6/7] Pasta '{mes_nome}' nao existe — criando...")
        pasta_mes = create_folder(service, mes_nome, pasta_ano['id'])
    print(f"  [6/7] {mes_nome} → {pasta_mes['id']}")

    # Nivel 7: Data (cria se nao existir)
    pasta_data = find_folder(service, date_str, pasta_mes['id'], drive_id)
    created = False
    if not pasta_data:
        print(f"  [7/7] Pasta '{date_str}' nao existe — criando...")
        pasta_data = create_folder(service, date_str, pasta_mes['id'])
        created = True
    print(f"  [7/7] {date_str} → {pasta_data['id']}")

    folder_link = pasta_data.get('webViewLink', f"https://drive.google.com/drive/folders/{pasta_data['id']}")

    return pasta_data['id'], folder_link, created


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description='Upload de PNGs do Figma para o Google Drive')
    parser.add_argument('--client', required=True, help='Nome da pasta do cliente no Drive (ex: "Stark")')
    parser.add_argument('--date', required=True, help='Data do frame no formato YYYY-MM-DD (ex: "2026-03-17")')
    parser.add_argument('--files', nargs='+', help='Caminhos dos arquivos PNG para upload (obrigatorio exceto com --dry-run)')
    parser.add_argument('--dry-run', action='store_true', help='Apenas navega as pastas, sem fazer upload')
    args = parser.parse_args()

    # Validar arquivos
    valid_files = []
    if args.files:
        for f in args.files:
            if not os.path.exists(f):
                print(f"AVISO: Arquivo nao encontrado, pulando: {f}", file=sys.stderr)
                continue
            valid_files.append(f)

    if not valid_files and not args.dry_run:
        print("ERRO: Nenhum arquivo valido para upload. Use --files ou --dry-run.", file=sys.stderr)
        sys.exit(1)

    print(f"\n📁 Upload Drive: {args.client} / {args.date}")
    print(f"   Arquivos: {len(valid_files)}\n")

    # Autenticar
    service = get_drive_service()

    # Navegar ate a pasta da data
    print("Navegando hierarquia de pastas...")
    folder_id, folder_link, created = navigate_to_date_folder(service, args.client, args.date)

    if created:
        print(f"\n✨ Pasta '{args.date}' criada automaticamente.")

    if args.dry_run:
        print(f"\n🔍 Dry run — pasta encontrada: {folder_link}")
        result = {
            'folder_id': folder_id,
            'folder_link': folder_link,
            'created': created,
            'files': [],
        }
        print(f"\n{json.dumps(result, indent=2)}")
        return

    # Upload dos arquivos
    print(f"\nFazendo upload de {len(valid_files)} arquivo(s)...")
    uploaded_files = []
    for i, file_path in enumerate(valid_files, 1):
        file_name = os.path.basename(file_path)
        print(f"  [{i}/{len(valid_files)}] {file_name}...", end=' ')
        uploaded = upload_file(service, file_path, folder_id)
        uploaded_files.append({
            'name': uploaded['name'],
            'id': uploaded['id'],
            'link': uploaded.get('webViewLink', ''),
        })
        print("OK")

    # Resultado
    result = {
        'folder_id': folder_id,
        'folder_link': folder_link,
        'created': created,
        'files': uploaded_files,
    }

    print(f"\n✅ Upload concluido!")
    print(f"📁 Pasta: {folder_link}")
    print(f"📎 Arquivos: {len(uploaded_files)}")
    print(f"\n{json.dumps(result, indent=2)}")


if __name__ == '__main__':
    main()
