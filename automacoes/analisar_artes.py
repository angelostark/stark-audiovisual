#!/usr/bin/env python3
"""
=====================================================================
ANALISAR ARTES — COLETA DE IMAGENS DO GOOGLE DRIVE
=====================================================================
Busca imagens do time AV no Shared Drive "Clientes" por data de
criacao (createdTime), filtra apenas membros do time, resolve o
cliente pela hierarquia de pastas e baixa para analise local.

Uso:
  python3 automacoes/analisar_artes.py \
    --client all --period today

  python3 automacoes/analisar_artes.py \
    --client all --date 2026-03-23

  python3 automacoes/analisar_artes.py \
    --client "Dr Felipe Salles" --period week --dry-run

Requer:
  pip install google-api-python-client google-auth
  Arquivo de credenciais: automacoes/credentials.json
  Drive Compartilhado "Clientes" acessivel pelo service account

Retorna JSON com lista de imagens baixadas e metadados.
=====================================================================
"""

import argparse
import io
import json
import os
import sys
from datetime import datetime, timedelta

from googleapiclient.http import MediaIoBaseDownload

from upload_drive import (
    get_drive_service,
    find_shared_drive,
    find_folder,
    find_folder_contains,
    find_content_folder,
    MESES,
    CONTENT_FOLDER_NAMES,
)

# =====================================================================
# CONFIGURACAO
# =====================================================================

ANALISE_SHEET_ID = '1fmOrGlXm6ZIdbu3rI2wpPTUtpNfluSM_XdJ8JyoTi0I'

IMAGE_MIMETYPES = [
    'image/png',
    'image/jpeg',
    'image/webp',
]

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB

# Time AV — identificacao por email/displayName do Drive
TEAM_EMAILS = {
    # Designers
    'humberto': 'Humberto',
    'joao': 'Joao',
    'eloy': 'Eloy',
    'max': 'Max',
    'karyne': 'Karyne',
    'milena': 'Milena',
    # Editores
    'ebertty': 'Ebertty',
    'andre': 'Andre',
    'mateus': 'Mateus',
}

TEAM_NAMES = set(TEAM_EMAILS.values())


# =====================================================================
# FUNCOES AUXILIARES
# =====================================================================

def resolve_period(period, date_str=None):
    """Converte period em lista de datas (strings YYYY-MM-DD)."""
    hoje = datetime.now()

    if date_str:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return [date_str]
        except ValueError:
            print(f"ERRO: Data invalida '{date_str}'. Use formato YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)

    if period == 'today':
        return [hoje.strftime('%Y-%m-%d')]
    elif period == 'week':
        segunda = hoje - timedelta(days=hoje.weekday())
        return [(segunda + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    elif period == 'month':
        primeiro_dia = hoje.replace(day=1)
        datas = []
        dia = primeiro_dia
        while dia.month == hoje.month:
            datas.append(dia.strftime('%Y-%m-%d'))
            dia += timedelta(days=1)
        return datas
    else:
        print(f"ERRO: Periodo invalido '{period}'. Use: today, week, month.", file=sys.stderr)
        sys.exit(1)


def identify_designer(file_metadata):
    """
    Identifica o designer pelo lastModifyingUser.
    Retorna nome do time ou None se nao for do time.
    """
    user = file_metadata.get('lastModifyingUser')
    if not user:
        return None

    email = user.get('emailAddress', '').lower()
    display_name = user.get('displayName', '').lower()

    for key, nome in TEAM_EMAILS.items():
        if key in email or key in display_name:
            return nome

    return None


def resolve_client_name(service, parent_id, drive_id, parent_cache):
    """Sobe a hierarquia de pastas ate achar a pasta-cliente (filha direta do Shared Drive)."""
    current_id = parent_id

    for _ in range(10):  # max depth
        if current_id == drive_id:
            return 'Desconhecido'

        if current_id in parent_cache:
            cached = parent_cache[current_id]
            if cached['parent_id'] == drive_id:
                return cached['name']
            current_id = cached['parent_id']
            continue

        try:
            meta = service.files().get(
                fileId=current_id,
                fields='id, name, parents',
                supportsAllDrives=True,
            ).execute()
        except Exception:
            return 'Desconhecido'

        parents = meta.get('parents', [])
        if not parents:
            return 'Desconhecido'

        gp_id = parents[0]
        parent_cache[current_id] = {'name': meta['name'], 'parent_id': gp_id}

        if gp_id == drive_id:
            return meta['name']

        current_id = gp_id

    return 'Desconhecido'


def search_team_images(service, drive_id, date_start, date_end):
    """Busca todas as imagens no Shared Drive por createdTime, filtra pelo time AV."""
    mime_conditions = " or ".join([f"mimeType = '{m}'" for m in IMAGE_MIMETYPES])
    query = (
        f"({mime_conditions}) "
        f"and createdTime >= '{date_start}T00:00:00' "
        f"and createdTime < '{date_end}T00:00:00' "
        f"and trashed = false"
    )

    all_files = []
    page_token = None
    while True:
        kwargs = {
            'q': query,
            'fields': 'nextPageToken, files(id, name, mimeType, size, parents, createdTime, webViewLink, lastModifyingUser)',
            'pageSize': 100,
            'supportsAllDrives': True,
            'includeItemsFromAllDrives': True,
            'driveId': drive_id,
            'corpora': 'drive',
        }
        if page_token:
            kwargs['pageToken'] = page_token
        results = service.files().list(**kwargs).execute()
        all_files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break

    # Filtrar apenas time AV
    team_files = []
    for f in all_files:
        designer = identify_designer(f)
        if designer:
            f['_designer'] = designer
            team_files.append(f)

    return team_files


def download_file(service, file_id, dest_path):
    """Baixa arquivo do Drive usando MediaIoBaseDownload."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    fh = io.FileIO(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.close()


# =====================================================================
# FUNCOES LEGADAS (usadas pela skill sob demanda)
# =====================================================================

def list_client_folders(service, parent_id, drive_id=None):
    """Lista pastas de clientes dentro do parent (Shared Drive Clientes)."""
    query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    query += f" and '{parent_id}' in parents"
    kwargs = {
        'q': query, 'fields': 'files(id, name)', 'pageSize': 200,
        'supportsAllDrives': True, 'includeItemsFromAllDrives': True, 'orderBy': 'name',
    }
    if drive_id:
        kwargs['driveId'] = drive_id
        kwargs['corpora'] = 'drive'
    results = service.files().list(**kwargs).execute()
    return results.get('files', [])


def navigate_to_artes_read_only(service, client_name, drive_id, clientes_id):
    """Navega ate a pasta Artes do cliente SEM criar pastas (legado)."""
    cliente = find_folder(service, client_name, clientes_id, drive_id)
    if not cliente:
        cliente = find_folder_contains(service, client_name, clientes_id, drive_id)
    if not cliente:
        return None, None, None, f"Pasta do cliente '{client_name}' nao encontrada"
    conteudo = find_content_folder(service, cliente['id'], drive_id)
    if not conteudo:
        return None, None, None, f"Pasta 'Cronograma de Conteudo' nao encontrada em '{client_name}'"
    artes = find_folder(service, 'Artes', conteudo['id'], drive_id)
    if not artes:
        artes = find_folder_contains(service, 'Artes', conteudo['id'], drive_id)
    if not artes:
        artes = find_folder_contains(service, 'ARTES', conteudo['id'], drive_id)
    if artes:
        return artes['id'], conteudo['id'], drive_id, None
    else:
        return None, conteudo['id'], drive_id, None


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description='Analisar Artes — Coleta de imagens do Google Drive')
    parser.add_argument('--client', required=True, help='Nome do cliente ou "all"')
    parser.add_argument('--period', default='week', choices=['today', 'week', 'month'],
                        help='Periodo de busca (default: week)')
    parser.add_argument('--date', help='Data especifica YYYY-MM-DD (sobrescreve --period)')
    parser.add_argument('--max-files', type=int, default=50, help='Limite de arquivos (default: 50)')
    parser.add_argument('--output-dir', default='/tmp/analise_artes', help='Diretorio destino')
    parser.add_argument('--dry-run', action='store_true', help='Lista sem baixar')
    parser.add_argument('--json-output', help='Salva JSON resultado em arquivo (default: stdout)')
    args = parser.parse_args()

    # Resolver datas
    dates = resolve_period(args.period, args.date)
    period_label = args.date if args.date else args.period

    print(f"\nAnalisar Artes: {args.client} / {period_label}")
    print(f"Datas: {', '.join(dates)}")
    if args.dry_run:
        print("(Dry-Run — nao vai baixar arquivos)\n")
    else:
        print()

    # Autenticar
    service = get_drive_service()

    # Shared Drive
    shared_drive = find_shared_drive(service, 'Clientes')
    if not shared_drive:
        print("ERRO: Shared Drive 'Clientes' nao encontrado.", file=sys.stderr)
        sys.exit(1)
    drive_id = shared_drive['id']
    print(f"  [1] Clientes (Shared Drive)")

    # Range de datas para query
    date_start = min(dates)
    date_end_dt = datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)
    date_end = date_end_dt.strftime('%Y-%m-%d')

    # Buscar imagens por createdTime + filtrar time AV
    print(f"  Buscando imagens criadas entre {date_start} e {date_end}...")
    team_files = search_team_images(service, drive_id, date_start, date_end)
    print(f"  Imagens do time AV: {len(team_files)}")

    if not team_files:
        result = {
            'client': args.client, 'period': period_label,
            'dates_searched': dates, 'total_images': 0,
            'skipped_files': [], 'images': [],
        }
        print("\nTotal: 0 imagens")
        if args.json_output:
            with open(args.json_output, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"JSON salvo em: {args.json_output}")
        else:
            print(f"\n{json.dumps(result, indent=2, ensure_ascii=False)}")
        return

    # Resolver cliente de cada arquivo (subindo hierarquia de pastas)
    print(f"  Resolvendo clientes...")
    parent_cache = {}
    for f in team_files:
        parents = f.get('parents', [])
        if parents:
            f['_client'] = resolve_client_name(service, parents[0], drive_id, parent_cache)
        else:
            f['_client'] = 'Desconhecido'

    # Filtrar por cliente se especificado
    if args.client.lower() != 'all':
        team_files = [f for f in team_files if args.client.lower() in f['_client'].lower()]
        print(f"  Filtrado para '{args.client}': {len(team_files)}")

    # Resumo por designer
    from collections import Counter
    designer_count = Counter(f['_designer'] for f in team_files)
    for nome, qtd in designer_count.most_common():
        print(f"    {nome}: {qtd} artes")

    # Aplicar limite
    if len(team_files) > args.max_files:
        print(f"  Limitando a {args.max_files} arquivos (de {len(team_files)})")
        team_files = team_files[:args.max_files]

    # Baixar e montar resultado
    all_images = []
    all_skipped = []

    for f in team_files:
        file_size = int(f.get('size', 0))
        client_name = f['_client']
        designer = f['_designer']
        created_date = f['createdTime'][:10]

        if file_size > MAX_FILE_SIZE_BYTES:
            all_skipped.append({
                'name': f['name'],
                'reason': f'muito grande ({file_size // (1024*1024)}MB)',
                'client': client_name,
                'date': created_date,
            })
            continue

        local_dir = os.path.join(args.output_dir, client_name, created_date)
        local_path = os.path.join(local_dir, f['name'])
        drive_link = f.get('webViewLink', f"https://drive.google.com/file/d/{f['id']}/view")

        image_info = {
            'name': f['name'],
            'file_id': f['id'],
            'drive_link': drive_link,
            'local_path': local_path,
            'designer': designer,
            'date_folder': created_date,
            'client': client_name,
            'size_kb': round(file_size / 1024),
        }

        if not args.dry_run:
            print(f"  [{client_name}] Baixando: {f['name']}...", end=' ')
            try:
                download_file(service, f['id'], local_path)
                print("OK")
            except Exception as e:
                print(f"ERRO: {e}")
                image_info['download_error'] = str(e)
        else:
            print(f"  [dry-run] [{client_name}] {f['name']} ({designer}, {image_info['size_kb']}KB)")

        all_images.append(image_info)

    # Output JSON
    result = {
        'client': args.client,
        'period': period_label,
        'dates_searched': dates,
        'total_images': len(all_images),
        'skipped_files': all_skipped,
        'images': all_images,
    }

    print(f"\nTotal: {len(all_images)} imagens, {len(all_skipped)} arquivos pulados")

    if args.json_output:
        with open(args.json_output, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"JSON salvo em: {args.json_output}")
    else:
        print(f"\n{json.dumps(result, indent=2, ensure_ascii=False)}")


if __name__ == '__main__':
    main()
