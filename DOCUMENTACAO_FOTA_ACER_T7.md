# Documentação Técnica: Extração de Firmware Oficial e Engenharia Reversa FOTA da Acer
## Acer Predator Connect Series (T7 / W6x / X7) — OpenWrt Research & Upstream

> **Bilingual Documentation / Documentação Bilíngue (PT-BR & EN-US)**  
> Este documento técnico e a ferramenta associada [`acer_fota_extractor.py`](file:///h:/FEITOS%20COM%20IA/Acer-Predator-Connect-T7/acer_fota_extractor.py) funcionam de forma **100% autônoma em qualquer computador (Windows, Linux, macOS)**. Não requer acesso físico ao roteador, nem Telnet/SSH ou estar na mesma rede. Conecta-se diretamente aos servidores oficiais da Acer (Cloud FOTA / AWS S3).
> 
> *This document and the companion script [`acer_fota_extractor.py`](file:///h:/FEITOS%20COM%20IA/Acer-Predator-Connect-T7/acer_fota_extractor.py) run **100% standalone on any PC, Linux, or Mac**. No physical router, SSH, or local connection is needed. It communicates directly with Acer Cloud FOTA and Amazon AWS S3.*

---

## 1. Plataformas e Modelos Analisados / Target Platforms

| Modelo | Processador / SoC | Arquitetura | Topologia Wi-Fi | Formato da Imagem Oficial |
| :--- | :--- | :--- | :--- | :--- |
| **Predator Connect T7** | Qualcomm IPQ5332 (AP-MI01.6) | ARM Cortex-A53 (AArch32 OEM) | Tri-Band Wi-Fi 7 BE11000 | FIT Image U-Boot SPI NAND 4K (`.img`) |
| **Predator Connect W6x** | MediaTek MT7986AV (Filogic 830) | ARM Cortex-A53 (AArch64) | Dual-Band Wi-Fi 6 AX6000 | MediaTek Dual-UBI SquashFS (`.bin`) |
| **Predator Connect X7** | Qualcomm IPQ5332 + 5G Modem | ARM Cortex-A53 | Tri-Band Wi-Fi 7 + 5G CPE | FIT Image U-Boot SPI NAND 4K (`.img`) |

---

## 2. Engenharia Reversa do Protocolo FOTA da Acer / FOTA Protocol Reverse Engineering

O binário nativo `/usr/bin/fota` presente no firmware original da Acer consulta a infraestrutura em nuvem através de chamadas HTTPS criptografadas.

### 2.1. Endpoints da API Oficial / Official API Endpoints
* **Timestamp Server (Unix epoch):**  
  `GET https://connect-ota.acervcon.com/now`
* **Transition Lookup & Version Query:**  
  `POST https://connect-ota.acervcon.com/updateVersion`

### 2.2. Autenticação e Criptografia do Token / Cryptographic Handshake
Toda requisição deve conter o cabeçalho HTTP `auth-token`. O token é um payload JSON cifrado com AES-256 no modo CBC:

$$\text{Plaintext} = \{\text{"project": } P, \text{ "deviceId": } D, \text{ "time": } T\}$$

* **Algoritmo:** AES-256-CBC com padding PKCS#7 (bloco de 128 bits).
* **Chave AES (`AES_KEY`):**  
  `4532374633324537464633303444374339463139443130303333423030333031`
* **Vetor de Inicialização (`AES_IV`):**  
  `38316331326462313565346563316236`
* **Codificação de Saída:** Base64 em linha única (sem quebras `\n`).

### 2.3. Lógica do Banco de Dados FOTA (Grafo de Transição de Estados)
* **Por que `00`, `01` ou wildcards (`*`) falham:**  
  O servidor da Acer não executa buscas relacionais abertas (`WHERE version >= ...`). O backend implementa uma **tabela estrita de transição de estados**:  
  $$(P_{\text{project}}, S_{\text{sku}}, V_{\text{source}}) \longrightarrow (V_{\text{target}}, \text{URL}_{\text{S3}}, \text{MD5}, \text{Size}, \text{Notes})$$  
  Se você enviar uma versão inexistente (ex.: `"00"` ou `"01"`), a chave não existe no banco e o servidor responde vazio:  
  `{"success": true, "firmware": ""}`.
* **A Estratégia de Mapeamento Completo:**  
  O script automatizado faz uma varredura em paralelo percorrendo todas as versões de release (`1.00.000001` até `1.01.000035`), descobrindo todas as imagens pré-assinadas da AWS S3 geradas com validade de 300 segundos.

---

## 3. Catálogo Completo de Firmwares e Changelogs Oficiais

### 3.1. Acer Predator Connect T7 (IPQ5332 Wi-Fi 7)
*Local de armazenamento local:* `Backups_MTD/Acer_Predator_Connect_T7/`

| Versão | Data de Release | Arquivo Oficial | Tamanho | MD5 Checksum | Changelog Oficial (`changeNotes`) |
| :---: | :---: | :--- | :---: | :--- | :--- |
| **1.00.000032** | 22/02/2024 | `nand-4k-ipq5332-single_100000032.img` | 55.06 MB | `22b426a7d6e63ae5a64a5e07008da975` | `0, upgrade to 1.00.000032` *(Última build linhagem v1.00)* |
| **1.01.000003** | 21/03/2024 | `nand-4k-ipq5332-single_101000003.img` | 56.06 MB | `0055cffc18bebd14c9a205c28a211538` | `1, update to 1.01.000003` |
| **1.01.000005** | 23/03/2024 | `nand-4k-ipq5332-single_101000005.img` | 56.06 MB | `ba8b3c3d867e1d62c9ab0c15badafd3e` | `1,update to 1.01.000005` |
| **1.01.000006** | 25/03/2024 | `nand-4k-ipq5332-single_101000006.img` | 56.06 MB | `2cffea9f71c4c8b671a5330a10408542` | `1, update to 1.01.000006` |
| **1.01.000007** | 08/04/2024 | `nand-4k-ipq5332-single_101000007.img` | 56.06 MB | `4868e36fabd5d1c77a80bc7e5a279ce2` | `1, update to 1.01.000007` |
| **1.01.000008** | 15/04/2024 | `nand-4k-ipq5332-single_101000008.img` | 56.06 MB | `55065f6821cfa2223d5aa81569b56e3e` | `1, update to 1.01.000008` *(Primeiro lote comercial global)* |
| **1.01.000009** | 18/04/2024 | `nand-4k-ipq5332-single_101000009.img` | 56.06 MB | `d0be0b26fce7c0f13e710b9a629b35b6` | `1, upgrade to 1.01.000009` |
| **1.01.000012** | 30/07/2024 | `nand-4k-ipq5332-single_101000012.img` | 54.31 MB | `731cdb77a7fefd1017a344fa5f8a1598` | `1,  OTA Test` *(Validação do sistema de entrega FOTA)* |
| **1.01.000024** | 20/01/2025 | `nand-4k-ipq5332-single_101000024.img` | 55.56 MB | `b65f93757cafd6a31f1fcd6a7d75fe3d` | `1, release 101000024` *(Versão Oficial Estável BR / TW)* |
| **1.01.000027** | 08/07/2025 | `nand-4k-ipq5332-single_101000027.img` | 55.31 MB | `d03578e8cd42dedd15fa9017e55e2161` | `1, release 101000027` *(Versão Oficial mais recente US)* |

### 3.2. Acer Predator Connect W6x (MT7986 Filogic 830)
*Local de armazenamento local:* `Backups_MTD/Acer_Predator_Connect_W6x/`

| Versão | Data de Release | Arquivo Oficial | Tamanho | MD5 Checksum | Changelog Oficial (`changeNotes`) |
| :---: | :---: | :--- | :---: | :--- | :--- |
| **1.00.000009** | 27/12/2023 | `W6x-1.00.000009.bin` | 31.96 MB | `f626ac4045708733bc84efe3459c0714` | `0,release v1.00.000009` *(Firmware inicial de fábrica)* |
| **1.00.000013** | 22/02/2024 | `W6x-1.00.000013.bin` | 34.90 MB | `dce4998e213d61e1913e9eda8c912b2c` | `1, update to 1.00.000013` |
| **1.00.000019** | 02/04/2024 | `W6x-1.00.000019.bin` | 38.96 MB | `4381e83acddc1b95b26ec3eb2b3dce9b` | `1, prepare for production image` |
| **1.00.000020** | 02/04/2024 | `W6x-1.00.000020_for_upgrade_test.bin` | 38.96 MB | `cbe3fc51141f51ed2f8c52ab86cc198c` | `1, test for OTA for BOBO,forece update` *(Build interno Acer)* |
| **1.00.000024** | 23/04/2024 | `W6x-1.00.000024.bin` | 35.68 MB | `305019b78663b9846cec382ee3fca554` | `1, prepare for production image ` |
| **1.00.000028** | 26/04/2024 | `W6x-1.00.000028.bin` | 35.68 MB | `0b47fb49a510e1aedcfae068a6f29c69` | `1, test for production image, force update` |
| **1.00.000032** | 06/05/2024 | `W6x-1.00.000032.bin` | 35.51 MB | `970e951e57652cf4f74a1e3dd20a002b` | `1, force update, FW for production ` |
| **1.00.000036** | 10/05/2024 | `W6x-1.00.000036.bin` | 35.51 MB | `ff9a53b85b9c5494284220780f47c718` | `1, Force update, Production image` |
| **1.01.000015** | 12/06/2025 | `W6x-1.01.000015.bin` | 35.71 MB | `153431824d713f8ba568aefa1aec3b90` | **`1,add vlan id`** *(Suporte a VLAN ID na WAN para operadoras)* |
| **2.00.000005** | 08/01/2026 | `W6x-2.00.000005_1391a60dc_enc.bin` | 36.12 MB | `eb973ce50635756a250b47dc1ca2bc28` | **`1, support mesh and bridge mode`** *(Major v2.0 Criptografada)* |

---

## 4. Como Executar o Extrator Autônomo / How to Run the Extractor

A ferramenta [`acer_fota_extractor.py`](file:///h:/FEITOS%20COM%20IA/Acer-Predator-Connect-T7/acer_fota_extractor.py) está pronta para uso em qualquer terminal.

### 4.1. Instalação de Dependências
```bash
pip install cryptography
```

### 4.2. Exemplos de Comandos (CLI Examples)

* **Listar todos os firmwares do Predator T7 com changelogs (sem baixar):**
  ```bash
  python acer_fota_extractor.py --model T7 --list
  ```

* **Baixar todas as versões do Predator T7 para uma pasta:**
  ```bash
  python acer_fota_extractor.py --model T7 --download --outdir ./Backups_MTD
  ```

* **Baixar apenas o firmware oficial de uma região específica (ex.: Brasil / BR):**
  ```bash
  python acer_fota_extractor.py --model T7 --sku BR --download
  ```

* **Baixar todas as versões do Predator W6x:**
  ```bash
  python acer_fota_extractor.py --model W6x --download --outdir ./Backups_MTD
  ```

* **Baixar todas as versões de todos os modelos (T7, W6x, X7) simultaneamente:**
  ```bash
  python acer_fota_extractor.py --model all --download --threads 12
  ```

---

## 5. Estrutura Interna da Imagem FIT do T7 (`nand-4k-ipq5332-single_*.img`)

A imagem oficial baixada é um container FIT Image padrão Qualcomm/U-Boot (Magic `0xD00DFEED`):

```
  [0x00] script       : flash.scr (Script U-Boot de particionamento e validação)
  [0x01] sbl1         : xbl_nand_4K.elf (Secondary Boot Loader Qualcomm)
  [0x02] mibib        : nand-system-partition-ipq5332-m4096-p256KiB.bin
  [0x03] bootconfig   : bootconfig.bin (Slot 1 / Slot 2 descriptor)
  [0x04] bootconfig1  : bootconfig.bin (Cópia espelho de segurança)
  [0x05] tz           : tz.mbn (Qualcomm QSEE / TrustZone)
  [0x06] devcfg       : devcfg.mbn (Device Configuration)
  [0x07] tme          : tmel-ipq53xx-patch.elf (Trust Management Engine)
  [0x08-0x19] ddr     : Tabelas CDT de DDR4 para plataformas Qualcomm
  [0x1A] u-boot       : openwrt-ipq5332-u-boot.mbn (Bootloader U-Boot 32-bit)
  [0x1B] ubi          : openwrt-ipq53xx-ipq53xx_32-ubi-root-m4096-p256KiB.img (52.5 MB)
```

Para extrair e inspecionar o container no Linux:
```bash
dumpimage -l nand-4k-ipq5332-single_101000024.img
dumpimage -T flat_dt -p 0x1B -o ubi_rootfs.img nand-4k-ipq5332-single_101000024.img
```

---

## 6. Diretrizes Técnicas para o Suporte Upstream no OpenWrt

1. **Isolamento de Dual-Boot (`bootconfig`):**
   * O `Slot 1` (`mtd21` / `rootfs`) deve permanecer 100% de fábrica como recuperação garantida (*failsafe*).
   * O OpenWrt comunitário deve ser instalado exclusivamente no `Slot 2` (`mtd20` / `rootfs_1`).
2. **Requisito Obrigatório do U-Boot `bootipq`:**
   * O volume `kernel` dentro do UBI precisa ser do tipo **`static`** (`UBI_STATIC_VOLUME`) com tamanho declarado exato (`-s <bytes>`). O bootloader da Acer rejeita e trava em loop se o volume for dinâmico.
3. **Preservação Crítica da Calibração de Rádio (`mtd18` / `0:ART`):**
   * A partição `0:ART` em `mtd18` (offset `0x01B80000`) contém os dados de calibração RF EEPROM exclusivos de cada unidade de hardware. Nunca deve ser sobrescrita.
