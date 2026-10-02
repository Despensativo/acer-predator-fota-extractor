#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
 Acer Predator Connect - Official Cloud FOTA Firmware Extractor & Downloader
 Extrator e Baixador de Firmwares Oficiais Acer Predator Connect (FOTA Cloud / AWS S3)
========================================================================================
 Supported Models / Modelos Suportados:
   - Acer Predator Connect T7  (Qualcomm IPQ5332 - Wi-Fi 7 BE11000)
   - Acer Predator Connect W6x (MediaTek MT7986 - Wi-Fi 6 AX6000)
   - Acer Predator Connect X7  (Qualcomm IPQ5332 - 5G CPE / Wi-Fi 7)

 Features / Recursos:
   - Modo Interativo / Interactive Wizard: Pergunta as opções passo a passo para o usuário!
   - Modo CLI Automatizado / Automated CLI Mode: Para scripts e pipelines de automação.
   - 100% Autônomo / Standalone: Não requer o roteador físico, roda em qualquer PC/Mac/Linux.
   - Bilíngue / Bilingual: Comentários e interface em PT-BR e EN-US.

 Requirements / Requisitos:
   pip install cryptography
========================================================================================
"""

import argparse
import base64
import hashlib
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# --------------------------------------------------------------------------------------
# Hardcoded Cryptographic Keys extracted from /usr/bin/fota
# Chaves criptográficas extraídas por engenharia reversa do binário /usr/bin/fota
# --------------------------------------------------------------------------------------
FOTA_GATEWAY = "https://connect-ota.acervcon.com"
AES_KEY = bytes.fromhex("4532374633324537464633303444374339463139443130303333423030333031")
AES_IV  = bytes.fromhex("38316331326462313565346563316236")

# Default valid production device IDs per model
# Números de série de produção válidos utilizados para handshake com a nuvem Acer
DEFAULT_DEVICE_IDS = {
    "T7":  "FFG2RTA007439002311L14",
    "W6x": "FFG2TTA007502007801N01",
    "X7":  "FFG2RTA007439002311L14",
}

# Known SKU regions per model
# Regiões / SKUs conhecidas para cada modelo
KNOWN_SKUS = {
    "T7":  ["BR", "US", "GBL", "TW", "EU", "WW", "PA", "default"],
    "W6x": ["GBL", "US", "EU", "TW", "BR", "default"],
    "X7":  ["GBL", "US", "EU", "TW", "BR", "default"],
}

# Known version ranges to scan in transition graph
# Faixas de versões para varredura completa no grafo de transição
VERSION_PROBES = [
    # 1.00.xxxxxx
    *[f"1.00.{i:06d}" for i in range(1, 35)],
    # 1.01.xxxxxx
    *[f"1.01.{i:06d}" for i in range(1, 35)],
    # 1.02.xxxxxx
    *[f"1.02.{i:06d}" for i in [1, 2, 5, 10, 15, 20]],
    # 2.00.xxxxxx (Major v2)
    *[f"2.00.{i:06d}" for i in [1, 2, 5, 10]],
]

# --------------------------------------------------------------------------------------
# Token & API Utilities / Funções Utilitárias de Token e API
# --------------------------------------------------------------------------------------
_cached_ts = 0
_cached_time_local = 0

def get_server_timestamp() -> int:
    """
    [EN] Fetches server timestamp from Acer /now endpoint.
    [PT-BR] Obtém o timestamp Unix atual do servidor /now da Acer.
    """
    global _cached_ts, _cached_time_local
    now = time.time()
    if now - _cached_time_local < 45 and _cached_ts > 0:
        return _cached_ts + int(now - _cached_time_local)
    try:
        req = urllib.request.Request(f"{FOTA_GATEWAY}/now", headers={"User-Agent": "curl/7.60.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            _cached_ts = int(data["timestamp"])
            _cached_time_local = now
            return _cached_ts
    except Exception:
        return int(time.time())

def generate_auth_token(project: str, device_id: str) -> str:
    """
    [EN] Generates AES-256-CBC PKCS#7 encrypted auth-token required by Acer FOTA API.
    [PT-BR] Gera o auth-token criptografado com AES-256-CBC PKCS#7 exigido pela API da Acer.
    """
    ts = get_server_timestamp()
    plaintext = f'{{\n "project":"{project}",\n "deviceId":"{device_id}",\n "time":{ts}\n}}\n'
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV))
    enc = cipher.encryptor()
    ciphertext = enc.update(padded) + enc.finalize()
    return base64.b64encode(ciphertext).decode("ascii")

def query_fota(project: str, sku: str, version: str, device_id: str) -> dict:
    """
    [EN] Queries Acer FOTA API for updates from (project, sku, version).
    [PT-BR] Consulta a API FOTA da Acer procurando transições a partir de (projeto, sku, versão).
    """
    token = generate_auth_token(project, device_id)
    body = {
        "projectName": project,
        "SKUName": sku,
        "version": version,
        "deviceId": device_id
    }
    req = urllib.request.Request(
        f"{FOTA_GATEWAY}/updateVersion",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json;charset=UTF-8",
            "auth-token": token,
            "User-Agent": "curl/7.60.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("success") and "firmware" in data and isinstance(data["firmware"], dict):
                fw = data["firmware"]
                if fw.get("firmwareUrl"):
                    return {
                        "project": project,
                        "sku": sku,
                        "queried_version": version,
                        "target_version": fw.get("version"),
                        "filename": fw.get("FirmwareName"),
                        "url": fw.get("firmwareUrl"),
                        "releaseDate": fw.get("releaseDate"),
                        "size": fw.get("size"),
                        "checksum": fw.get("checksum"),
                        "changeNotes": fw.get("changeNotes", "").strip()
                    }
    except Exception:
        pass
    return None

def verify_file_md5(filepath: str, expected_md5: str) -> bool:
    """
    [EN] Computes file MD5 hash and compares with expected value.
    [PT-BR] Calcula o hash MD5 do arquivo e compara com o valor esperado.
    """
    if not os.path.exists(filepath):
        return False
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().lower() == expected_md5.lower()

# --------------------------------------------------------------------------------------
# Download Manager / Gerenciador de Download
# --------------------------------------------------------------------------------------
def download_firmware(item: dict, output_dir: str, device_id: str) -> bool:
    """
    [EN] Downloads firmware with live progress bar and validates MD5 checksum.
    [PT-BR] Baixa o firmware com barra de progresso em tempo real e valida o checksum MD5.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = item["filename"]
    dest_path = os.path.join(output_dir, filename)
    expected_md5 = item["checksum"]
    expected_size = item["size"]

    if os.path.exists(dest_path):
        if verify_file_md5(dest_path, expected_md5):
            print(f"  [JA EXISTE / ALREADY EXISTS] {filename} (MD5 OK)")
            return True

    # Request fresh presigned URL in case original expired
    sku = item["sku"] if isinstance(item["sku"], str) else item["skus"][0]
    trigger_v = item.get("queried_version") or item.get("source_versions_trigger", ["1.01.000012"])[0]
    
    fresh_info = query_fota(item["project"], sku, trigger_v, device_id)
    url = fresh_info["url"] if fresh_info else item.get("url")

    if not url:
        print(f"  [ERRO / ERROR] Could not retrieve S3 download URL for {filename}")
        return False

    tmp_path = dest_path + ".download"
    print(f"  [BAIXANDO / DOWNLOADING] {filename} ({expected_size / 1024 / 1024:.2f} MB)...")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.60.0"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(tmp_path, "wb") as out:
            dl = 0
            while True:
                buf = resp.read(512 * 1024)
                if not buf:
                    break
                out.write(buf)
                dl += len(buf)
                pct = (dl / expected_size) * 100 if expected_size > 0 else 0
                print(f"\r    Progresso: {dl / 1024 / 1024:.1f} MB / {expected_size / 1024 / 1024:.1f} MB ({pct:.1f}%)", end="", flush=True)

        print()
        if verify_file_md5(tmp_path, expected_md5):
            if os.path.exists(dest_path):
                os.remove(dest_path)
            os.rename(tmp_path, dest_path)
            print(f"  [SUCESSO 100%] Salvo e verificado com sucesso: {dest_path}")
            return True
        else:
            print(f"  [FALHA DE MD5] Checksum divergente para {filename}!")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return False
    except Exception as e:
        print(f"  [ERRO] Falha no download: {e}")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False

# --------------------------------------------------------------------------------------
# Scanning Logic / Lógica de Varredura
# --------------------------------------------------------------------------------------
def scan_models(models: list, skus_filter: list = None, workers: int = 8) -> dict:
    """
    [EN] High-speed multithreaded scanning of Acer FOTA version transition graph.
    [PT-BR] Varredura multithread de alta velocidade no grafo de versões do FOTA da Acer.
    """
    tasks = []
    for model in models:
        dev_id = DEFAULT_DEVICE_IDS.get(model, DEFAULT_DEVICE_IDS["T7"])
        target_skus = skus_filter if skus_filter else KNOWN_SKUS.get(model, ["default"])
        for sku in target_skus:
            for v in VERSION_PROBES:
                tasks.append((model, sku, v, dev_id))

    print(f"\n[*] Consultando servidor FOTA ({len(tasks)} requisições em {workers} threads paralelas)...")
    print(f"[*] Querying Acer FOTA server ({len(tasks)} requests across {workers} parallel threads)...\n")

    catalog = {}
    done = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(query_fota, m, s, v, d): (m, s, v) for m, s, v, d in tasks}
        for future in as_completed(future_map):
            done += 1
            if done % 100 == 0 or done == len(tasks):
                print(f"    Progresso / Progress: {done}/{len(tasks)} consultas concluídas...", flush=True)
            res = future.result()
            if res:
                key = f"{res['project']}_{res['target_version']}_{res['checksum']}"
                if key not in catalog:
                    catalog[key] = {
                        "project": res["project"],
                        "target_version": res["target_version"],
                        "filename": res["filename"],
                        "url": res["url"],
                        "releaseDate": res["releaseDate"],
                        "size": res["size"],
                        "checksum": res["checksum"],
                        "changeNotes": res["changeNotes"],
                        "skus": [res["sku"]],
                        "source_versions_trigger": [res["queried_version"]]
                    }
                    print(f"  [+] DESCOBERTO: [{res['project']}] v{res['target_version']} ({res['filename']}) - {res['changeNotes']}")
                else:
                    if res["sku"] not in catalog[key]["skus"]:
                        catalog[key]["skus"].append(res["sku"])
                    if res["queried_version"] not in catalog[key]["source_versions_trigger"]:
                        catalog[key]["source_versions_trigger"].append(res["queried_version"])

    return catalog

# --------------------------------------------------------------------------------------
# Interactive Wizard / Assistente Interativo Passo a Passo
# --------------------------------------------------------------------------------------
def interactive_wizard():
    """
    [EN] Step-by-step interactive questionnaire for users.
    [PT-BR] Questionário interativo passo a passo para preenchimento fácil pelo usuário.
    """
    print("\n" + "=" * 80)
    print("      ACER PREDATOR CONNECT — ASSISTENTE INTERATIVO DE FIRMWARES")
    print("      ACER PREDATOR CONNECT — INTERACTIVE FIRMWARE WIZARD")
    print("=" * 80)

    # 1. Idioma / Language
    print("\nEscolha o idioma da interface / Choose your language:")
    print("  [1] Português (Brasil)")
    print("  [2] English")
    lang_choice = input("Opção / Option [1/2] (padrão: 1): ").strip()
    is_pt = lang_choice != "2"

    # 2. Modelo / Model
    if is_pt:
        print("\n--- PASSO 1: Escolha o modelo do seu roteador Acer Predator ---")
        print("  [1] Acer Predator Connect T7  (Wi-Fi 7 BE11000 - Qualcomm IPQ5332)")
        print("  [2] Acer Predator Connect W6x (Wi-Fi 6 AX6000 - MediaTek MT7986)")
        print("  [3] Acer Predator Connect X7  (Wi-Fi 7 + 5G CPE - Qualcomm IPQ5332)")
        print("  [4] TODOS OS MODELOS (Varredura Completa)")
        mod_in = input("Escolha uma opção [1-4] (padrão: 1): ").strip()
    else:
        print("\n--- STEP 1: Choose your Acer Predator router model ---")
        print("  [1] Acer Predator Connect T7  (Wi-Fi 7 BE11000 - Qualcomm IPQ5332)")
        print("  [2] Acer Predator Connect W6x (Wi-Fi 6 AX6000 - MediaTek MT7986)")
        print("  [3] Acer Predator Connect X7  (Wi-Fi 7 + 5G CPE - Qualcomm IPQ5332)")
        print("  [4] ALL MODELS (Full Scan)")
        mod_in = input("Choose an option [1-4] (default: 1): ").strip()

    model_map = {"1": "T7", "2": "W6x", "3": "X7", "4": "all"}
    chosen_model = model_map.get(mod_in, "T7")
    models = ["T7", "W6x", "X7"] if chosen_model == "all" else [chosen_model]

    # 3. Ação / Action
    if is_pt:
        print("\n--- PASSO 2: O que você deseja fazer? ---")
        print("  [1] Baixar TODAS as versões encontradas (Recomendado para arquivamento e backup)")
        print("  [2] Baixar apenas a versão mais recente oficial")
        print("  [3] Apenas listar as versões e changelogs na tela (sem baixar nada)")
        act_in = input("Escolha uma opção [1-3] (padrão: 1): ").strip()
    else:
        print("\n--- STEP 2: What would you like to do? ---")
        print("  [1] Download ALL discovered versions (Recommended for complete backup)")
        print("  [2] Download only the LATEST official release")
        print("  [3] Only list versions & changelogs on screen (no download)")
        act_in = input("Choose an option [1-3] (default: 1): ").strip()

    mode = "all" if act_in == "1" else ("latest" if act_in == "2" else "list")

    # 4. Região / SKU
    if is_pt:
        print("\n--- PASSO 3: Região / SKU do aparelho ---")
        print("  [1] Todas as regiões disponíveis (Brasil, Estados Unidos, Global, Taiwan, etc.)")
        print("  [2] Brasil (BR)")
        print("  [3] Estados Unidos (US)")
        print("  [4] Global (GBL)")
        print("  [5] Taiwan (TW)")
        sku_in = input("Escolha uma opção [1-5] (padrão: 1): ").strip()
    else:
        print("\n--- STEP 3: Region / Hardware SKU ---")
        print("  [1] All available regions (Brazil, US, Global, Taiwan, etc.)")
        print("  [2] Brazil (BR)")
        print("  [3] United States (US)")
        print("  [4] Global (GBL)")
        print("  [5] Taiwan (TW)")
        sku_in = input("Choose an option [1-5] (default: 1): ").strip()

    sku_map = {"1": None, "2": ["BR"], "3": ["US"], "4": ["GBL"], "5": ["TW"]}
    chosen_skus = sku_map.get(sku_in, None)

    # 5. Diretório de Destino / Output Directory
    default_dir = "./firmwares_oficiais"
    if mode != "list":
        if is_pt:
            dir_in = input(f"\n--- PASSO 4: Onde deseja salvar os arquivos? [Padrão: {default_dir}]: ").strip()
        else:
            dir_in = input(f"\n--- STEP 4: Destination folder for downloads? [Default: {default_dir}]: ").strip()
        outdir = dir_in if dir_in else default_dir
    else:
        outdir = default_dir

    # 6. Resumo e Confirmação / Summary & Confirmation
    print("\n" + "=" * 80)
    if is_pt:
        print("RESUMO DA SOLICITAÇÃO:")
        print(f"  * Modelo(s):       {', '.join(models)}")
        print(f"  * Região / SKU:    {chosen_skus[0] if chosen_skus else 'Todas as regiões'}")
        print(f"  * Ação:            {'Baixar todas as versões' if mode == 'all' else ('Baixar mais recente' if mode == 'latest' else 'Apenas listar')}")
        if mode != "list":
            print(f"  * Pasta de Saída:  {outdir}")
        conf = input("\nDeseja iniciar a operação agora? [S/n]: ").strip().lower()
    else:
        print("OPERATION SUMMARY:")
        print(f"  * Model(s):        {', '.join(models)}")
        print(f"  * Region / SKU:    {chosen_skus[0] if chosen_skus else 'All regions'}")
        print(f"  * Action:          {'Download all versions' if mode == 'all' else ('Download latest version only' if mode == 'latest' else 'List only')}")
        if mode != "list":
            print(f"  * Output Folder:   {outdir}")
        conf = input("\nStart operation now? [Y/n]: ").strip().lower()

    if conf in ["n", "no", "nao", "não"]:
        print("Operação cancelada pelo usuário. / Operation cancelled by user.")
        return

    # Executa a varredura
    catalog = scan_models(models, skus_filter=chosen_skus, workers=10)

    # Exibe tabela resumo
    print("\n" + "=" * 90)
    print("               SUMMARY OF DISCOVERED FIRMWARES / RESUMO DAS VERSÕES")
    print("=" * 90)
    print(f"{'Model':<6} | {'Version':<13} | {'Date':<10} | {'Size':<9} | {'SKUs':<12} | {'Change Notes / Changelog'}")
    print("-" * 90)
    for k, item in sorted(catalog.items(), key=lambda x: (x[1]['project'], x[1]['target_version'])):
        skus_str = ",".join(item["skus"][:3])
        size_str = f"{item['size']/1024/1024:.1f} MB"
        print(f"{item['project']:<6} | {item['target_version']:<13} | {item['releaseDate']:<10} | {size_str:<9} | {skus_str:<12} | {item['changeNotes']}")
    print("=" * 90)

    # Processa downloads se solicitado
    if mode in ["all", "latest"]:
        # Se for apenas a mais recente, filtra o catálogo para a maior versão de cada modelo/sku
        items_to_download = []
        if mode == "latest":
            latest_by_model = {}
            for item in catalog.values():
                proj = item["project"]
                if proj not in latest_by_model or item["target_version"] > latest_by_model[proj]["target_version"]:
                    latest_by_model[proj] = item
            items_to_download = list(latest_by_model.values())
        else:
            items_to_download = list(catalog.values())

        if is_pt:
            print(f"\n[*] Iniciando download de {len(items_to_download)} arquivos para '{outdir}'...")
        else:
            print(f"\n[*] Starting download of {len(items_to_download)} files to '{outdir}'...")

        success = 0
        for item in items_to_download:
            dev_id = DEFAULT_DEVICE_IDS.get(item["project"], DEFAULT_DEVICE_IDS["T7"])
            model_dir = os.path.join(outdir, f"Acer_Predator_{item['project']}")
            if download_firmware(item, model_dir, dev_id):
                success += 1

        print("\n" + "=" * 80)
        if is_pt:
            print(f"🎉 CONCLUÍDO COM SUCESSO! {success}/{len(items_to_download)} firmwares salvos e verificados com MD5.")
            print(f"📁 Os arquivos estão armazenados em: {os.path.abspath(outdir)}")
        else:
            print(f"🎉 COMPLETED SUCCESSFULLY! {success}/{len(items_to_download)} firmwares saved and verified with MD5.")
            print(f"📁 Files stored in: {os.path.abspath(outdir)}")
        print("=" * 80)

# --------------------------------------------------------------------------------------
# CLI Interface / Interface de Linha de Comando Tradicional
# --------------------------------------------------------------------------------------
def main():
    # If launched with no arguments, open the interactive wizard!
    # Se executado sem argumentos, abre automaticamente o assistente interativo com perguntas!
    if len(sys.argv) == 1:
        interactive_wizard()
        return

    parser = argparse.ArgumentParser(
        description="Acer Predator Connect Official Cloud FOTA Firmware Extractor (PT-BR / EN-US)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / Exemplos de Uso:
  python acer_fota_extractor.py                 # Abre o assistente interativo com perguntas!
  python acer_fota_extractor.py --interactive   # Força o modo interativo
  python acer_fota_extractor.py --model T7 --list
  python acer_fota_extractor.py --model W6x --download --outdir ./Backups_MTD
  python acer_fota_extractor.py --model all --download --outdir ./Backups_MTD
        """
    )
    parser.add_argument("-i", "--interactive", "--wizard", action="store_true",
                        help="Launch step-by-step interactive questionnaire / Inicia o assistente com perguntas")
    parser.add_argument("--model", choices=["T7", "W6x", "X7", "all"], default="T7",
                        help="Target router model / Modelo do roteador alvo (default: T7)")
    parser.add_argument("--sku", default=None,
                        help="Specific SKU/Region filter (e.g. BR, US, GBL) / Região específica")
    parser.add_argument("--list", action="store_true",
                        help="Only list all discovered firmwares and changelogs without downloading / Apenas listar sem baixar")
    parser.add_argument("--download", action="store_true",
                        help="Download all discovered firmwares / Baixar todos os firmwares encontrados")
    parser.add_argument("--outdir", default="./firmwares_oficiais",
                        help="Destination directory for downloads / Diretório de destino (default: ./firmwares_oficiais)")
    parser.add_argument("--threads", type=int, default=10,
                        help="Parallel worker threads / Número de threads simultâneas (default: 10)")
    parser.add_argument("--save-catalog", default="catalogo_firmwares_acer.json",
                        help="Path to save JSON catalog / Caminho para salvar o catálogo JSON")

    args = parser.parse_args()

    if args.interactive:
        interactive_wizard()
        return

    models = ["T7", "W6x", "X7"] if args.model == "all" else [args.model]
    skus = [args.sku] if args.sku else None

    print("=" * 80)
    print(" ACER PREDATOR CONNECT - CLOUD FOTA EXTRACTOR & REVERSE ENGINEERING TOOL")
    print(" FERRAMENTA DE EXTRAÇÃO E ENGENHARIA REVERSA FOTA ACER PREDATOR CONNECT")
    print("=" * 80)
    print(f"Models / Modelos: {', '.join(models)}")
    print(f"SKUs: {args.sku or 'All known / Todas conhecidas'}")
    print(f"Mode / Modo: {'DOWNLOAD' if args.download else 'LIST ONLY / APENAS LISTAR'}")
    print(f"Output Directory / Destino: {args.outdir}")

    catalog = scan_models(models, skus_filter=skus, workers=args.threads)

    with open(args.save_catalog, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Catalog saved to / Catálogo salvo em: {args.save_catalog}")

    print("\n" + "=" * 90)
    print("               SUMMARY OF DISCOVERED FIRMWARES / RESUMO DAS VERSÕES")
    print("=" * 90)
    print(f"{'Model':<6} | {'Version':<13} | {'Date':<10} | {'Size':<9} | {'SKUs':<12} | {'Change Notes / Changelog'}")
    print("-" * 90)
    for k, item in sorted(catalog.items(), key=lambda x: (x[1]['project'], x[1]['target_version'])):
        skus_str = ",".join(item["skus"][:3])
        size_str = f"{item['size']/1024/1024:.1f} MB"
        print(f"{item['project']:<6} | {item['target_version']:<13} | {item['releaseDate']:<10} | {size_str:<9} | {skus_str:<12} | {item['changeNotes']}")
    print("=" * 90)

    if args.download:
        print(f"\n[*] Starting download of {len(catalog)} firmware images to '{args.outdir}'...")
        print(f"[*] Iniciando download de {len(catalog)} imagens para '{args.outdir}'...\n")
        success = 0
        for item in catalog.values():
            dev_id = DEFAULT_DEVICE_IDS.get(item["project"], DEFAULT_DEVICE_IDS["T7"])
            model_dir = os.path.join(args.outdir, f"Acer_Predator_{item['project']}")
            if download_firmware(item, model_dir, dev_id):
                success += 1

        print(f"\n[+] Processo concluído: {success}/{len(catalog)} firmwares verificados 100%!")
        print(f"[+] Download process finished: {success}/{len(catalog)} firmwares verified 100%!")

if __name__ == "__main__":
    main()
