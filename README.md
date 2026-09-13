<div align="center">

# Ancient-Bench: A Comprehensive Multi-millennial, Multi-medium, and Multi-script Benchmark for Ancient Chinese Artifact Text Recognition

[![Paper](https://img.shields.io/badge/arXiv-2608.27169-B31B1B.svg)](https://arxiv.org/abs/2608.27169)
[![Dataset HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-blue)](YOUR_HUGGINGFACE_LINK_HERE)
[![Baidu Netdisk](https://img.shields.io/badge/Baidu%20Netdisk-%E7%99%BE%E5%BA%A6%E7%BD%91%E7%9B%98-06A7FF)](https://pan.baidu.com/s/1Vx8vllHY51wT8aSOa_kGXA?pwd=54su)

**English** | [**中文简体**](README_zh.md)

</div>

---

### 🚨 Crucial Notice
> **Strictly for Academic Research Use Only.**  
> The images in this dataset are curated from publicly accessible archives of official cultural heritage institutions (e.g., museums and libraries). The authors claim no copyright over the original images. Users must strictly comply with the corresponding institutional terms and licenses. Any commercial use is strictly prohibited.

---

## 📥 Dataset Access

| Platform | Link | Extraction Code / Notes |
| :--- | :--- | :---: |
| **Baidu Netdisk (百度网盘)** | [🔗 Click to Download from Baidu Netdisk](https://pan.baidu.com/s/1Vx8vllHY51wT8aSOa_kGXA?pwd=54su) | **`54su`** |
| **Hugging Face** | [🤗 Dataset Repository](YOUR_HUGGINGFACE_LINK_HERE) | Direct Access |

---

## 📌 Overview

**Ancient-Bench** (Accepted by **EMNLP 2026**) is the first comprehensive, multi-millennial, multi-medium, and multi-script benchmark tailored for ancient Chinese artifact text recognition. It comprises **2,700 meticulously annotated high-resolution images**, spanning **3,000+ years** of Chinese script evolution, covering **9 heterogeneous artifact categories** from 14 national-level cultural institutions, and encompassing **7 historical script forms**.

To establish an objective and unified evaluation across heterogeneous media, Ancient-Bench defines three standardization protocols: **Symbol Standardization**, **Character Standardization**, and **Parsing Standardization**.

<p align="center">
  <img src="figure/main.png" alt="Ancient-Bench Overview" width="95%"/>
</p>

## ✨ Key Features

1. **Multi-millennial (3,000+ Years):** Spans the entire evolutionary trajectory of Chinese writing, divided into three major historical eras:
   - **Early Civilization Period (1200 – 221 BCE):** Oracle bones, ritual bronzes, early bamboo slips, and silk manuscripts.
   - **Imperial Medieval & Stone Inscription Age (221 BCE – 900 CE):** Official seals, stone steles, epitaphs, and cliff inscriptions.
   - **Early Modern Printing & Artistic Maturity Period (900 – 1911 CE):** Woodblock editions and paper calligraphy works.
2. **Multi-medium (9 Artifact Categories):** Oracle Bones, Bronzes, Bamboo/Wooden Slips, Silk Manuscripts, Seals, Steles, Cliff Inscriptions, Ancient Editions, and Calligraphy.
3. **Multi-script (7 Mainstream Scripts):** Oracle Bone Script, Bronze Script, Seal Script, Clerical Script, Regular Script, Cursive Script, and Running Script.
4. **Authoritative & Diverse Provenance:** Sourced from 14 national-level cultural heritage institutions and authentic in-the-wild cliff inscriptions.

## 📊 Dataset Statistics

<p align="center">
  <img src="figure/statistics.png" alt="Ancient-Bench Dataset Statistics" width="95%"/>
</p>

| Medium | Images | Resolution Range (px) | Chars / Image | Institutions | Script Types Covered |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Oracle** (甲骨) | 300 | 600×800 | 1–68 | 1 | Oracle Bone |
| **Bronze** (金文) | 250 | 41×80 – 1024×1024 | 1–77 | 2 | Bronze |
| **Slip** (简牍) | 300 | 29×224 – 700×6820 | 1–107 | 3 | Seal, Clerical |
| **Silk** (帛书) | 300 | 46×124 – 1330×2067 | 1–784 | 2 | Seal, Clerical |
| **Seal** (印章) | 350 | 100×150 – 1333×1341 | 1–40 | 4 | Oracle, Bronze, Seal |
| **Steles** (碑帖) | 300 | 85×155 – 5795×16745 | 4–816 | 4 | Seal, Clerical, Regular, Running |
| **Cliff** (摩崖) | 200 | 183×113 – 7300×5760 | 2–216 | In-the-wild | Seal, Clerical, Regular, Running |
| **Edition** (刻本) | 300 | 751×506 – 970×2817 | 4–776 | 1 | Seal, Clerical, Regular, Cursive, Running |
| **Calligraphy** (书法) | 400 | 303×509 – 4802×13385 | 2–1666 | 4 | Bronze, Seal, Clerical, Regular, Cursive, Running |
| **Total** | **2,700** | **41×80 – 5795×16745** | **1–1666** | **14 + In-the-wild** | **All 7 Scripts** |

## 📐 Standardization Protocols

- **Symbol Standardization:** Preserves historical typographic marks as-is (`=` and `-` for repetition/ligatures; `~` for transpositions; `□` for unreadable damaged characters; `<unrecognizable>` for unencoded characters).
- **Character Standardization:** Uses scholarly clerical transcription (隶定) with traditional characters as reference; strictly complies with the *“what you see is what you get”* (WYSIWYG) principle to avoid semantic distortion from modern simplification.
- **Parsing Standardization:** Preserves reading hierarchy and column-by-column orders; explicitly tags double-line interlinear notes using `（）`, non-transcription areas (center seam, book ears) using `<ignore>`, and margin notes using `<note>`.

---

## ⚖️ Ethical Statement & Copyright

1. **Academic Use Only:** Ancient-Bench is constructed strictly for academic research and algorithm benchmarking. Commercial use in any form is prohibited.
2. **Image Copyright:** Images in Ancient-Bench are collected from publicly accessible online repositories of museums, libraries, and cultural heritage institutions. The authors do not claim or transfer any copyright over these artifacts or source images.
3. **Compliance:** Researchers downloading this dataset must strictly comply with the terms of service and licensing of the respective cultural institutions.

---

## 📖 Citation

If you find **Ancient-Bench** helpful in your research, please cite our EMNLP 2026 paper:

```bibtex
@inproceedings{cheng2026ancientbench,
  title={Ancient-Bench: A Comprehensive Multi-millennial, Multi-medium, and Multi-script Benchmark for Ancient Chinese Artifact Text Recognition},
  author={Cheng, Hiuyi and Xu, Nuo and Zhang, Yuyi and Zheng, Xuhan and Pan, Wei and Zhang, Jing and Peng, Dezhi and Liao, Minghui and Teng, Yihua and Wu, Jihao and Ren, Haoyu and Jin, Lianwen},
  booktitle={Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year={2026},
  url={https://arxiv.org/abs/2608.27169}
}
