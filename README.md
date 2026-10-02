# Acer Predator Connect — Official Cloud FOTA Firmware Extractor
## Extrator e Baixador de Firmwares Oficiais da Linha Acer Predator Connect (FOTA / AWS S3)

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenWrt Support](https://img.shields.io/badge/OpenWrt-Research-orange.svg)](https://openwrt.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

> **Bilingual Documentation / Documentação Bilíngue (PT-BR & EN-US)**  
> This tool is **100% standalone** and runs on any computer (Windows, Linux, macOS).  
> **No physical router, SSH, or local connection is needed.** It communicates directly with Acer's official cloud update infrastructure (`https://connect-ota.acervcon.com`) and Amazon AWS S3.
> 
> *Esta ferramenta roda **100% de forma autônoma** no seu PC/Linux/Mac. **Não requer o roteador físico conectado**.*

---

## 🚀 Supported Models / Modelos Suportados

| Model / Modelo | SoC / Processor | Architecture | Wi-Fi Topology | Official Image Format |
| :--- | :--- | :--- | :--- | :--- |
| **Predator Connect T7** | Qualcomm IPQ5332 (AP-MI01.6) | ARM Cortex-A53 | Tri-Band Wi-Fi 7 (BE11000) | FIT Image U-Boot SPI NAND 4K (`.img`) |
| **Predator Connect W6x** | MediaTek MT7986AV (Filogic 830) | ARM Cortex-A53 | Dual-Band Wi-Fi 6 (AX6000) | MediaTek Dual-UBI SquashFS (`.bin`) |
| **Predator Connect X7** | Qualcomm IPQ5332 + 5G Modem | ARM Cortex-A53 | Tri-Band Wi-Fi 7 + 5G CPE | FIT Image U-Boot SPI NAND 4K (`.img`) |

---

## 🛠️ Features / Recursos

* **100% Standalone:** Runs on any PC/Server with Python 3 and Internet access.
* **Cryptographic Handshake:** Implements the official AES-256-CBC PKCS#7 authentication reverse-engineered from `/usr/bin/fota`.
* **State Transition Scanner:** Probes the Acer Cloud database across version spaces (`1.00.xxxxxx`, `1.01.xxxxxx`, `2.00.xxxxxx`) to discover all past, present, and staging builds.
* **Official Changelogs:** Captures original internal engineering release notes (`changeNotes`) straight from Acer's cloud database.
* **Automatic Integrity Verification:** Computes and verifies MD5 checksums of all downloaded packages against Acer's official hashes.
* **High-Speed Multithreading:** Parallel worker threads for rapid discovery.

---

## 📦 Installation / Instalação

```bash
# Clone the repository / Clonar o repositório
git clone https://github.com/Despensativo/acer-predator-fota-extractor.git
cd acer-predator-fota-extractor

# Install dependencies / Instalar dependências
pip install -r requirements.txt
```

---

## 💻 Usage / Como Usar

### 🎮 Modo Interativo (Assistente com Perguntas Passo a Passo)
Se preferir não digitar parâmetros de linha de comando, basta rodar o script diretamente:
```bash
python acer_fota_extractor.py
```
O script fará um questionário na tela passo a passo:
1. **Idioma:** Português (Brasil) ou English
2. **Modelo:** Predator T7, W6x, X7 ou Todos
3. **Ação:** Baixar todas as versões, apenas a mais recente ou apenas listar na tela
4. **Região / SKU:** Brasil (BR), EUA (US), Global (GBL), etc.
5. **Pasta de destino:** Onde salvar os arquivos no seu computador

---

### ⚡ Modo Linha de Comando (CLI Automatizado)
```bash
# List all firmwares for Predator T7
python acer_fota_extractor.py --model T7 --list

# List all firmwares for Predator W6x
python acer_fota_extractor.py --model W6x --list
```

### 2. Download Firmwares / Baixar Imagens
```bash
# Download all versions of Predator T7 into a folder
python acer_fota_extractor.py --model T7 --download --outdir ./firmwares

# Download all versions of Predator W6x
python acer_fota_extractor.py --model W6x --download --outdir ./firmwares

# Download a specific regional SKU (e.g. Brazil / BR)
python acer_fota_extractor.py --model T7 --sku BR --download --outdir ./firmwares

# Download all models (T7, W6x, X7) with 12 parallel threads
python acer_fota_extractor.py --model all --download --threads 12 --outdir ./firmwares
```

---

## 🔐 Cryptography & Protocol Details / Engenharia Reversa

The Acer `/usr/bin/fota` client generates a temporary `auth-token` header for every request:

1. **Timestamp Request:**
   `GET https://connect-ota.acervcon.com/now` -> Unix timestamp $T$.
2. **Payload Construction:**
   ```json
   {
    "project": "<MODEL>",
    "deviceId": "<SERIAL_NUMBER>",
    "time": <TIMESTAMP>
   }
   ```
3. **AES-256-CBC Encryption:**
   * **Key:** `4532374633324537464633303444374339463139443130303333423030333031`
   * **IV:** `38316331326462313565346563316236`
   * **Padding:** PKCS#7 (128-bit block).
   * **Encoding:** Single-line Base64.
4. **Transition Query:**
   `POST https://connect-ota.acervcon.com/updateVersion`
   Returns Amazon AWS S3 presigned download URLs with 300-second TTL.

---

## 📋 Catalog of Discovered Firmwares / Catálogo de Versões

### Acer Predator Connect T7
| Version | Release Date | Official File | MD5 Checksum | Notes / Changelog |
| :---: | :---: | :--- | :--- | :--- |
| **1.00.000032** | 2024-02-22 | `nand-4k-ipq5332-single_100000032.img` | `22b426a7d6e63ae5a64a5e07008da975` | `0, upgrade to 1.00.000032` *(Last v1.00 pre-release)* |
| **1.01.000008** | 2024-04-15 | `nand-4k-ipq5332-single_101000008.img` | `55065f6821cfa2223d5aa81569b56e3e` | `1, update to 1.01.000008` *(Launch factory build)* |
| **1.01.000012** | 2024-07-30 | `nand-4k-ipq5332-single_101000012.img` | `731cdb77a7fefd1017a344fa5f8a1598` | `1,  OTA Test` |
| **1.01.000024** | 2025-01-20 | `nand-4k-ipq5332-single_101000024.img` | `b65f93757cafd6a31f1fcd6a7d75fe3d` | `1, release 101000024` *(Brazil / Taiwan Stable)* |
| **1.01.000027** | 2025-07-08 | `nand-4k-ipq5332-single_101000027.img` | `d03578e8cd42dedd15fa9017e55e2161` | `1, release 101000027` *(North America Latest)* |

### Acer Predator Connect W6x
| Version | Release Date | Official File | MD5 Checksum | Notes / Changelog |
| :---: | :---: | :--- | :--- | :--- |
| **1.00.000009** | 2023-12-27 | `W6x-1.00.000009.bin` | `f626ac4045708733bc84efe3459c0714` | `0,release v1.00.000009` *(Factory launch)* |
| **1.00.000020** | 2024-04-02 | `W6x-1.00.000020_for_upgrade_test.bin` | `cbe3fc51141f51ed2f8c52ab86cc198c` | `1, test for OTA for BOBO,forece update` *(Internal lab build)* |
| **1.00.000036** | 2024-05-10 | `W6x-1.00.000036.bin` | `ff9a53b85b9c5494284220780f47c718` | `1, Force update, Production image` |
| **1.01.000015** | 2025-06-12 | `W6x-1.01.000015.bin` | `153431824d713f8ba568aefa1aec3b90` | **`1,add vlan id`** *(ISP VLAN ID tagging support)* |
| **2.00.000005** | 2026-01-08 | `W6x-2.00.000005_1391a60dc_enc.bin` | `eb973ce50635756a250b47dc1ca2bc28` | **`1, support mesh and bridge mode`** *(Major v2.0 Encrypted)* |

---

## 🛡️ License & Disclaimer

* **License:** [MIT License](LICENSE).
* **Disclaimer:** This project is intended solely for research, firmware recovery, interoperability, and OpenWrt open-source development. All trademarks and firmware binaries belong to their respective owners.
