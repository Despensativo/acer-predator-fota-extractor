<p align="center">
  <img src="assets/banner.png" alt="Acer Predator Connect FOTA Extractor" width="100%">
</p>

<h1 align="center">Acer Predator Connect — FOTA Firmware Extractor</h1>

<p align="center">
  <strong>Ferramenta autônoma de extração e download de firmwares oficiais direto da nuvem da Acer (AWS S3)</strong><br>
  <em>Standalone official firmware extractor and downloader directly from Acer Cloud FOTA (AWS S3)</em>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://openwrt.org"><img src="https://img.shields.io/badge/OpenWrt-Research-orange.svg?style=for-the-badge&logo=openwrt&logoColor=white" alt="OpenWrt Research"></a>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg?style=for-the-badge" alt="Platform">
</p>

---

## ⚡ O que é esta ferramenta? / What is this tool?

O **Acer Predator Connect FOTA Extractor** é uma ferramenta de engenharia reversa que se conecta diretamente aos servidores de atualização em nuvem da Acer (`connect-ota.acervcon.com`) e da Amazon AWS S3 para **descobrir, validar e baixar qualquer versão oficial de firmware** da linha de roteadores gamer Acer Predator Connect.

### 🌟 Diferenciais Principais / Key Highlights:
* 🖥️ **100% Autônomo:** Roda no seu PC (Windows, Linux ou Mac). **Não precisa do roteador conectado** nem de cabo de rede, SSH ou Telnet.
* 🎮 **Assistente Interativo Passo a Passo:** Basta abrir o script e ele faz perguntas simples na tela para baixar a ROM certa.
* 🏷️ **Suporte a Modelos Personalizados:** Funciona tanto nos modelos pré-configurados quanto em qualquer outro modelo de rede da Acer inserindo o código (ex: `W6`, `X5`, `W6m`).
* 🔒 **Autenticação Criptográfica Oficial:** Implementa o handshake AES-256-CBC nativo extraído do binário `/usr/bin/fota`.
* 🛡️ **Integridade Garantida (MD5):** Valida automaticamente o checksum criptográfico de cada imagem baixada.
* 📝 **Changelogs da Engenharia:** Extrai as notas de versão oficiais inseridas pela equipe de desenvolvimento da Acer.

---

## 🎯 Modelos Suportados / Supported Models

| Modelo / Model | Processador / SoC | Wi-Fi / Tecnologias | Formato do Arquivo |
| :--- | :--- | :--- | :--- |
| **Predator Connect T7** | Qualcomm IPQ5332 (AP-MI01.6) | Tri-Band Wi-Fi 7 (BE11000) | Imagem FIT U-Boot SPI NAND 4K (`.img`) |
| **Predator Connect W6x** | MediaTek MT7986AV (Filogic 830) | Dual-Band Wi-Fi 6 (AX6000) | Dual-UBI NAND SquashFS (`.bin`) |
| **Predator Connect X7** | Qualcomm IPQ5332 + 5G Modem | Tri-Band Wi-Fi 7 + 5G CPE | Imagem FIT U-Boot SPI NAND 4K (`.img`) |
| **Outros / Custom** | W6 (Wi-Fi 6E), X5 (5G), W6m (Mesh) | Modelos personalizados Acer | Automático pelo S/N e SKU |

---

## 🚀 Como Usar em 3 Passos / Quick Start

### 1. Instalar as dependências
```bash
git clone https://github.com/Despensativo/acer-predator-fota-extractor.git
cd acer-predator-fota-extractor
pip install -r requirements.txt
```

### 2. Rodar o assistente interativo (Recomendado)
Basta executar o script sem parâmetros:
```bash
python acer_fota_extractor.py
```
O assistente fará perguntas na tela:
1. **Idioma:** Português (Brasil) ou English
2. **Modelo:** Digitar o seu próprio modelo ou escolher T7, W6x ou X7
3. **Ação:** Baixar a versão mais recente, baixar todas ou apenas listar
4. **Região / SKU:** Brasil (BR), EUA (US), Global (GBL) ou todas
5. **Pasta de destino:** Onde salvar os arquivos no seu computador

---

## 💻 Modo Linha de Comando / CLI Automation

Para scripts e pipelines automatizados, use os parâmetros de linha de comando:

```bash
# Listar todos os firmwares do Predator T7 com changelogs (sem baixar)
python acer_fota_extractor.py --model T7 --list

# Baixar o firmware mais recente do Predator T7 oficial do Brasil (BR)
python acer_fota_extractor.py --model T7 --sku BR --download

# Baixar todas as versões do Predator W6x para uma pasta personalizada
python acer_fota_extractor.py --model W6x --download --outdir ./Backups_W6x

# Consultar um modelo personalizado com seu próprio número de série (S/N da etiqueta)
python acer_fota_extractor.py --model W6 --device-id FFG2ETA001234567890 --download
```

---

## 📋 Catálogo de Firmwares Mapeados / Discovered Versions

### Acer Predator Connect T7
| Versão | Data de Release | Arquivo Oficial | MD5 Checksum | Notas da Engenharia (`changeNotes`) |
| :---: | :---: | :--- | :--- | :--- |
| **1.00.000032** | 22/02/2024 | `nand-4k-ipq5332-single_100000032.img` | `22b426a7d6e63ae5a64a5e07008da975` | `0, upgrade to 1.00.000032` *(Pré-lançamento)* |
| **1.01.000008** | 15/04/2024 | `nand-4k-ipq5332-single_101000008.img` | `55065f6821cfa2223d5aa81569b56e3e` | `1, update to 1.01.000008` *(Primeiro lote de fábrica)* |
| **1.01.000012** | 30/07/2024 | `nand-4k-ipq5332-single_101000012.img` | `731cdb77a7fefd1017a344fa5f8a1598` | `1,  OTA Test` |
| **1.01.000024** | 20/01/2025 | `nand-4k-ipq5332-single_101000024.img` | `b65f93757cafd6a31f1fcd6a7d75fe3d` | `1, release 101000024` *(Estável Brasil / Taiwan)* |
| **1.01.000027** | 08/07/2025 | `nand-4k-ipq5332-single_101000027.img` | `d03578e8cd42dedd15fa9017e55e2161` | `1, release 101000027` *(Mais recente América do Norte)* |

### Acer Predator Connect W6x
| Versão | Data de Release | Arquivo Oficial | MD5 Checksum | Notas da Engenharia (`changeNotes`) |
| :---: | :---: | :--- | :--- | :--- |
| **1.00.000009** | 27/12/2023 | `W6x-1.00.000009.bin` | `f626ac4045708733bc84efe3459c0714` | `0,release v1.00.000009` *(Firmware inicial de fábrica)* |
| **1.00.000020** | 02/04/2024 | `W6x-1.00.000020_for_upgrade_test.bin` | `cbe3fc51141f51ed2f8c52ab86cc198c` | `1, test for OTA for BOBO,forece update` *(Build interno)* |
| **1.00.000036** | 10/05/2024 | `W6x-1.00.000036.bin` | `ff9a53b85b9c5494284220780f47c718` | `1, Force update, Production image` |
| **1.01.000015** | 12/06/2025 | `W6x-1.01.000015.bin` | `153431824d713f8ba568aefa1aec3b90` | **`1,add vlan id`** *(Suporte a VLAN ID na WAN)* |
| **2.00.000005** | 08/01/2026 | `W6x-2.00.000005_1391a60dc_enc.bin` | `eb973ce50635756a250b47dc1ca2bc28` | **`1, support mesh and bridge mode`** *(Major v2.0)* |

---

## 🏷️ Tags & Tópicos Sugeridos para o Repositório no GitHub
Para facilitar que a comunidade encontre o repositório nas pesquisas do GitHub e Google, adicione estas tags na seção **Topics / About** do repositório:

`openwrt` · `acer-predator` · `firmware-extractor` · `fota` · `ipq5332` · `mt7986` · `wi-fi-7` · `wi-fi-6` · `reverse-engineering` · `router-recovery` · `stock-firmware` · `aws-s3-downloader` · `embedded-linux`

---

## 🛡️ Licença / License & Disclaimer
* **Licença:** Distribuído sob a licença [MIT](LICENSE).
* **Disclaimer:** Ferramenta desenvolvida exclusivamente para pesquisa, recuperação de roteadores brickados, interoperabilidade e desenvolvimento comunitário de código aberto para o OpenWrt. Todas as marcas e firmwares pertencem à Acer Inc. e seus parceiros.
