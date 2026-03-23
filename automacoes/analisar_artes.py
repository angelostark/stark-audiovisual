#!/usr/bin/env python3
"""
=====================================================================
ANALISAR ARTES — COLETA DE IMAGENS DO GOOGLE DRIVE
=====================================================================
Navega a hierarquia de pastas do cliente no Drive (Shared Drives),
lista e baixa imagens (PNG/JPG/WEBP) de pastas de data para analise.

Uso:
  python3 automacoes/analisar_artes.py \
    --client "Stark" --period week

  python3 automacoes/analisar_artes.py \
    --client "Stark" --date 2026-03-17

  python3 automacoes/analisar_artes.py \
    --client "Stark" --period today --dry-run

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

# Planilha "Analise de Artes - AV" no Google Sheets
ANALISE_SHEET_ID = '1fmOrGlXm6ZIdbu3rI2wpPTUtpNfluSM_XdJ8JyoTi0I'

IMAGE_MIMETYPES = [
    'image/png',
    'image/jpeg',
    'image/webp',
]

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB

# Mapa de email do service account / time → nome do designer
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


def list_client_folders(service, parent_id, drive_id=None):
    """Lista pastas de clientes dentro do parent (Shared Drive Clientes)."""
    query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    query += f" and '{parent_id}' in parents"

    kwargs = {
        'q': query,
        'fields': 'files(id, name)',
        'pageSize': 200,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
        'orderBy': 'name',
    }
    if drive_id:
        kwargs['driveId'] = drive_id
        kwargs['corpora'] = 'drive'

    results = service.files().list(**kwargs).execute()
    return results.get('files', [])


def navigate_to_artes_read_only(service, client_name, drive_id, clientes_id):
    """
    Navega ate a pasta Artes do cliente SEM criar pastas.
    Retorna (artes_folder_id, artes_parent_id, drive_id) ou (None, None, None) se nao encontrar.
    """
    # Nivel 2: Cliente
    cliente = find_folder(service, client_name, clientes_id, drive_id)
    if not cliente:
        cliente = find_folder_contains(service, client_name, clientes_id, drive_id)
    if not cliente:
        return None, None, None, f"Pasta do cliente '{client_name}' nao encontrada"

    # Nivel 3: Cronograma de Conteudo
    conteudo = find_content_folder(service, cliente['id'], drive_id)
    if not conteudo:
        return None, None, None, f"Pasta 'Cronograma de Conteudo' nao encontrada em '{client_name}'"

    # Nivel 4: Artes (pode nao existir como nivel separado)
    artes = find_folder(service, 'Artes', conteudo['id'], drive_id)
    if not artes:
        artes = find_folder_contains(service, 'Artes', conteudo['id'], drive_id)
    if not artes:
        artes = find_folder_contains(service, 'ARTES', conteudo['id'], drive_id)

    if artes:
        return artes['id'], conteudo['id'], drive_id, None
    else:
        # Sem pasta Artes — ano pode estar direto no Conteudo
        return None, conteudo['id'], drive_id, None


def find_date_folders_in_range(service, parent_id, drive_id, dates):
    """
    Busca pastas de data no range dentro da hierarquia Artes > ano > mes > data.
    Suporta dois formatos de nome de pasta:
      - YYYY-MM-DD (ex: 2026-03-17)
      - DD.MM ou DD.MM Tipo (ex: 17.03, 18.03 Carrossel)
    Retorna lista de {folder_id, date_str, folder_name}.
    """
    found = []

    # Agrupar datas por ano e mes
    dates_by_year_month = {}
    for d in dates:
        parts = d.split('-')
        ano = parts[0]
        mes_num = int(parts[1])
        mes_nome = MESES.get(mes_num)
        if not mes_nome:
            continue
        key = (ano, mes_nome, mes_num)
        if key not in dates_by_year_month:
            dates_by_year_month[key] = []
        dates_by_year_month[key].append(d)

    for (ano, mes_nome, mes_num), date_list in dates_by_year_month.items():
        # Buscar pasta do ano
        pasta_ano = find_folder(service, ano, parent_id, drive_id)
        if not pasta_ano:
            continue

        # Buscar pasta do mes
        pasta_mes = find_folder(service, mes_nome, pasta_ano['id'], drive_id)
        if not pasta_mes:
            continue

        # Buscar pastas de data (tenta multiplos formatos)
        for date_str in date_list:
            dia = date_str.split('-')[2]  # "17" de "2026-03-17"
            dia_sem_zero = str(int(dia))   # "17" (remove zero a esquerda se houver)
            mes_str = f"{mes_num:02d}"     # "03"

            # Formato 1: YYYY-MM-DD (ex: 2026-03-17)
            pasta_data = find_folder(service, date_str, pasta_mes['id'], drive_id)

            # Formato 2: DD.MM (ex: 17.03)
            if not pasta_data:
                pasta_data = find_folder(service, f"{dia}.{mes_str}", pasta_mes['id'], drive_id)

            # Formato 3: D.MM sem zero (ex: 7.03)
            if not pasta_data:
                pasta_data = find_folder(service, f"{dia_sem_zero}.{mes_str}", pasta_mes['id'], drive_id)

            # Formato 4: DD.MM Tipo (ex: 18.03 Carrossel) — busca parcial
            if not pasta_data:
                pasta_data = find_folder_contains(service, f"{dia}.{mes_str}", pasta_mes['id'], drive_id)

            if pasta_data:
                found.append({
                    'folder_id': pasta_data['id'],
                    'date_str': date_str,
                    'folder_name': pasta_data['name'],
                })

    return found


def list_image_files(service, folder_id, drive_id=None):
    """Lista arquivos de imagem (PNG/JPG/WEBP) em uma pasta."""
    mime_conditions = " or ".join([f"mimeType = '{m}'" for m in IMAGE_MIMETYPES])
    query = f"({mime_conditions}) and '{folder_id}' in parents and trashed = false"

    kwargs = {
        'q': query,
        'fields': 'files(id, name, mimeType, size, webViewLink, lastModifyingUser)',
        'pageSize': 100,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
    }
    if drive_id:
        kwargs['driveId'] = drive_id
        kwargs['corpora'] = 'drive'

    results = service.files().list(**kwargs).execute()
    return results.get('files', [])


def list_all_files_in_folder(service, folder_id, drive_id=None):
    """Lista TODOS os arquivos (nao-pastas) em uma pasta, para detectar skipped."""
    query = f"'{folder_id}' in parents and trashed = false and mimeType != 'application/vnd.google-apps.folder'"

    kwargs = {
        'q': query,
        'fields': 'files(id, name, mimeType, size)',
        'pageSize': 100,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
    }
    if drive_id:
        kwargs['driveId'] = drive_id
        kwargs['corpora'] = 'drive'

    results = service.files().list(**kwargs).execute()
    return results.get('files', [])


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


def identify_designer(file_metadata):
    """
    Identifica o designer pelo lastModifyingUser.
    Retorna nome do time ou 'Desconhecido'.
    """
    user = file_metadata.get('lastModifyingUser')
    if not user:
        return 'Desconhecido'

    email = user.get('emailAddress', '').lower()
    display_name = user.get('displayName', '').lower()

    # Tentar match por email ou displayName
    for key, nome in TEAM_EMAILS.items():
        if key in email or key in display_name:
            return nome

    # Se nao reconheceu, retorna o displayName original ou Desconhecido
    if user.get('displayName'):
        return user['displayName']

    return 'Desconhecido'


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

    # Nivel 1: Shared Drive Clientes
    drive_id = None
    shared_drive = find_shared_drive(service, 'Clientes')
    if shared_drive:
        clientes_id = shared_drive['id']
        drive_id = shared_drive['id']
        print(f"  [1] Clientes (Shared Drive)")
    else:
        query = "name = 'Clientes' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(
            q=query, fields='files(id, name)', pageSize=5,
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute()
        files = results.get('files', [])
        if not files:
            print("ERRO: Pasta/Drive 'Clientes' nao encontrado.", file=sys.stderr)
            sys.exit(1)
        clientes_id = files[0]['id']
        print(f"  [1] Clientes (pasta)")

    # Determinar lista de clientes
    if args.client.lower() == 'all':
        client_folders = list_client_folders(service, clientes_id, drive_id)
        client_names = [f['name'] for f in client_folders]
        print(f"  Clientes encontrados: {len(client_names)}")
    else:
        client_names = [args.client]

    all_images = []
    all_skipped = []
    total_downloaded = 0

    for client_name in client_names:
        print(f"\n  Processando: {client_name}")

        # Navegar ate Artes
        artes_id, parent_id, d_id, error = navigate_to_artes_read_only(
            service, client_name, drive_id, clientes_id
        )

        if error:
            print(f"    AVISO: {error} — pulando")
            continue

        # Se achou Artes, buscar a partir dela; senao, buscar a partir do parent (Conteudo)
        search_parent = artes_id if artes_id else parent_id

        # Buscar pastas de data
        date_folders = find_date_folders_in_range(service, search_parent, d_id, dates)

        if not date_folders:
            print(f"    Nenhuma pasta de data encontrada no range")
            continue

        print(f"    Pastas de data encontradas: {len(date_folders)}")

        for df in date_folders:
            if total_downloaded >= args.max_files:
                print(f"    Limite de {args.max_files} arquivos atingido")
                break

            folder_id = df['folder_id']
            date_str = df['date_str']

            # Listar imagens
            images = list_image_files(service, folder_id, d_id)

            # Listar todos os arquivos para detectar skipped
            all_files = list_all_files_in_folder(service, folder_id, d_id)
            for f in all_files:
                if f['mimeType'] not in IMAGE_MIMETYPES:
                    all_skipped.append({
                        'name': f['name'],
                        'reason': f['mimeType'],
                        'client': client_name,
                        'date': date_str,
                    })

            for img in images:
                if total_downloaded >= args.max_files:
                    break

                file_size = int(img.get('size', 0))
                if file_size > MAX_FILE_SIZE_BYTES:
                    all_skipped.append({
                        'name': img['name'],
                        'reason': f'muito grande ({file_size // (1024*1024)}MB)',
                        'client': client_name,
                        'date': date_str,
                    })
                    continue

                designer = identify_designer(img)

                # Caminho local
                local_dir = os.path.join(args.output_dir, client_name, date_str)
                local_path = os.path.join(local_dir, img['name'])

                drive_link = img.get('webViewLink', f"https://drive.google.com/file/d/{img['id']}/view")

                image_info = {
                    'name': img['name'],
                    'file_id': img['id'],
                    'drive_link': drive_link,
                    'local_path': local_path,
                    'designer': designer,
                    'date_folder': date_str,
                    'client': client_name,
                    'size_kb': round(file_size / 1024),
                }

                if not args.dry_run:
                    print(f"      Baixando: {img['name']}...", end=' ')
                    try:
                        download_file(service, img['id'], local_path)
                        print("OK")
                    except Exception as e:
                        print(f"ERRO: {e}")
                        image_info['download_error'] = str(e)
                else:
                    print(f"      [dry-run] {img['name']} ({designer}, {image_info['size_kb']}KB)")

                all_images.append(image_info)
                total_downloaded += 1

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
