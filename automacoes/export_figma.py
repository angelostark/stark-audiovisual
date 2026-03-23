#!/usr/bin/env python3
"""
=====================================================================
EXPORT DE FRAMES DO FIGMA — FLUXO FIGMA → DRIVE
=====================================================================
Usa a API REST do Figma para exportar frames como PNG em alta qualidade.

Uso:
  python3 automacoes/export_figma.py \
    --file-key "042FZHjPyx1TWMO4kzx1ai" \
    --node-ids "1038:6" "1038:16" "1038:19" \
    --prefix "2026-03-17-Oi" \
    --output /tmp/figma_exports

  # Com token via argumento (alternativa a variavel de ambiente):
  python3 automacoes/export_figma.py \
    --token "figd_..." \
    --file-key "042FZHjPyx1TWMO4kzx1ai" \
    --node-ids "1038:6" \
    --prefix "2026-03-17-Oi"

Requer:
  pip install requests
  FIGMA_TOKEN como variavel de ambiente ou via --token

Retorna JSON:
  {
    "files": [
      {"name": "2026-03-17-Oi-card-01.png", "path": "/tmp/figma_exports/..."}
    ]
  }
=====================================================================
"""

import argparse
import json
import os
import sys
import requests

# =====================================================================
# CONFIGURACAO
# =====================================================================

FIGMA_API_BASE = 'https://api.figma.com/v1'
DEFAULT_OUTPUT = '/tmp/figma_exports'
DEFAULT_SCALE = 2  # 2x para alta qualidade


# =====================================================================
# FUNCOES
# =====================================================================

def get_token(args_token=None):
    """Obtem o token do Figma (argumento > env > erro)."""
    token = args_token or os.environ.get('FIGMA_TOKEN')
    if not token:
        print("ERRO: Token do Figma nao encontrado.", file=sys.stderr)
        print("Defina FIGMA_TOKEN como variavel de ambiente ou use --token.", file=sys.stderr)
        print("Gere em: Figma → Settings → Personal Access Tokens", file=sys.stderr)
        sys.exit(1)
    return token


def export_nodes_batch(token, file_key, node_ids, scale=DEFAULT_SCALE):
    """Chama a API do Figma para exportar um lote de nodes como PNG. Retorna dict {nodeId: url}."""
    ids_param = ','.join(node_ids)
    url = f"{FIGMA_API_BASE}/images/{file_key}"
    params = {
        'ids': ids_param,
        'format': 'png',
        'scale': scale,
    }
    headers = {
        'X-Figma-Token': token,
    }

    resp = requests.get(url, params=params, headers=headers)

    if resp.status_code != 200:
        error_text = resp.text
        # Detectar render timeout para retry com lote menor
        if 'timeout' in error_text.lower() or resp.status_code == 400:
            return None, error_text
        print(f"ERRO: API do Figma retornou {resp.status_code}", file=sys.stderr)
        print(error_text, file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    if data.get('err'):
        if 'timeout' in str(data['err']).lower():
            return None, data['err']
        print(f"ERRO: {data['err']}", file=sys.stderr)
        sys.exit(1)

    return data.get('images', {}), None


def export_nodes(token, file_key, node_ids, scale=DEFAULT_SCALE, batch_size=5):
    """Exporta nodes em lotes para evitar render timeout. Retorna dict {nodeId: url}."""
    all_images = {}

    if len(node_ids) <= batch_size:
        # Tenta tudo de uma vez primeiro
        print(f"  Solicitando export de {len(node_ids)} frames (scale={scale}x)...")
        images, error = export_nodes_batch(token, file_key, node_ids, scale)
        if images is not None:
            return images
        # Timeout com lote pequeno — tenta um por um
        print(f"  ⚠️  Timeout com {len(node_ids)} frames. Exportando um por um...")
        for node_id in node_ids:
            images, error = export_nodes_batch(token, file_key, [node_id], scale)
            if images:
                all_images.update(images)
            else:
                print(f"  ⚠️  Timeout no node {node_id}, pulando.", file=sys.stderr)
        return all_images

    # Mais nodes que o batch_size — dividir em lotes
    import math
    num_batches = math.ceil(len(node_ids) / batch_size)
    print(f"  Solicitando export de {len(node_ids)} frames em {num_batches} lotes (scale={scale}x)...")

    for batch_num in range(num_batches):
        start = batch_num * batch_size
        end = start + batch_size
        batch = node_ids[start:end]
        print(f"    Lote {batch_num + 1}/{num_batches} ({len(batch)} frames)...", end=' ')

        images, error = export_nodes_batch(token, file_key, batch, scale)
        if images is not None:
            all_images.update(images)
            print("OK")
        else:
            print(f"Timeout — tentando um por um...")
            for node_id in batch:
                images, error = export_nodes_batch(token, file_key, [node_id], scale)
                if images:
                    all_images.update(images)
                else:
                    print(f"    ⚠️  Timeout no node {node_id}, pulando.", file=sys.stderr)

    return all_images


def download_image(url, output_path):
    """Baixa uma imagem de uma URL e salva no caminho especificado."""
    resp = requests.get(url, stream=True)
    if resp.status_code != 200:
        print(f"ERRO ao baixar: {resp.status_code}", file=sys.stderr)
        return False

    with open(output_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return True


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description='Exportar frames do Figma como PNG')
    parser.add_argument('--token', help='Figma Personal Access Token (alternativa a FIGMA_TOKEN env)')
    parser.add_argument('--file-key', required=True, help='File key do Figma')
    parser.add_argument('--node-ids', required=True, nargs='+', help='Node IDs para exportar (ex: "1038:6" "1038:16")')
    parser.add_argument('--prefix', default='export', help='Prefixo dos arquivos (ex: "2026-03-17-Oi")')
    parser.add_argument('--output', default=DEFAULT_OUTPUT, help=f'Diretorio de saida (default: {DEFAULT_OUTPUT})')
    parser.add_argument('--scale', type=int, default=DEFAULT_SCALE, help=f'Escala do export (default: {DEFAULT_SCALE})')
    parser.add_argument('--batch-size', type=int, default=5, help='Frames por lote para evitar timeout (default: 5)')
    args = parser.parse_args()

    token = get_token(args.token)

    # Criar diretorio de saida
    os.makedirs(args.output, exist_ok=True)

    print(f"\n🎨 Figma Export: {args.prefix}")
    print(f"   Frames: {len(args.node_ids)}")
    print(f"   Scale: {args.scale}x\n")

    # Solicitar URLs de export (em lotes para evitar timeout)
    image_urls = export_nodes(token, args.file_key, args.node_ids, args.scale, args.batch_size)

    # Baixar cada imagem
    downloaded = []
    total = len(args.node_ids)

    for i, node_id in enumerate(args.node_ids, 1):
        url = image_urls.get(node_id)
        if not url:
            print(f"  [{i}/{total}] {node_id} — sem URL, pulando", file=sys.stderr)
            continue

        # Nomear arquivo: prefixo-card-01.png, prefixo-card-02.png...
        if total == 1:
            filename = f"{args.prefix}.png"
        else:
            filename = f"{args.prefix}-card-{i:02d}.png"

        output_path = os.path.join(args.output, filename)
        print(f"  [{i}/{total}] {filename}...", end=' ')

        if download_image(url, output_path):
            size_kb = os.path.getsize(output_path) / 1024
            downloaded.append({
                'name': filename,
                'path': output_path,
                'node_id': node_id,
                'size_kb': round(size_kb, 1),
            })
            print(f"OK ({size_kb:.0f} KB)")
        else:
            print("FALHOU")

    # Resultado
    result = {
        'prefix': args.prefix,
        'output_dir': args.output,
        'total_requested': total,
        'total_downloaded': len(downloaded),
        'files': downloaded,
    }

    print(f"\n✅ Export concluido: {len(downloaded)}/{total} frames")
    print(f"📁 Salvos em: {args.output}")
    print(f"\n{json.dumps(result, indent=2)}")


if __name__ == '__main__':
    main()
