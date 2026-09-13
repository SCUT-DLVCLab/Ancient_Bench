# Ancient-Bench Evaluation Toolkit

<p align="center">
  <b>English</b> | <a href="README_zh.md">简体中文</a>
</p>

Evaluation script for the Ancient-Bench, covering **9 artifact carriers**: oracle bones, bronzes, bamboo/wooden slips, silk manuscripts, seals, stele rubbings, cliff carvings, book editions, and calligraphy.

The repo ships the **real benchmark annotations plus predictions from two demo models** (2,700 samples across 9 categories). Clone it, run `python run.py`, and the full pipeline completes.

---

## 1. Quick Start

```bash
pip install pyyaml python-Levenshtein pandas tqdm openpyxl opencc-python-reimplemented

python run.py
```

Output:

```
[INFO] ✅ 评测完成
[INFO] LaTeX: evaluate_results/evaluation_table_latex.txt
[INFO] Excel: evaluate_results/evaluation_table.xlsx
[INFO] JSON : evaluate_results/evaluation_report.json
```

Example result (`evaluation_table_latex.txt`):

```
Model & Oracle & Bronze & Slip & Silk & Seal & Stele & Cliff & Editions & Calligraphy & Overall \\
demo-model-a & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 \\
demo-model-b & 0.92 / 0.95 & 0.89 / 0.94 & 0.86 / 0.92 & 0.84 / 0.91 & 0.86 / 0.92 & 0.81 / 0.90 & 0.88 / 0.93 & 0.77 / 0.87 & 0.81 / 0.90 & 0.85 / 0.92 \\
```

---

## 2. Directory Layout

```
.
├── run.py                      # evaluation script
├── config.yaml                 # config (the only file you edit)
│
├── Ancient_Bench/              # ← gt_dir: ground truth
│   ├── oracle_bone_artifacts/
│   │   └── conv.jsonl
│   ├── bronze_rubbings/
│   │   └── conv.jsonl
│   └── ...                     # 9 categories total
│
├── infer_results/              # ← root_dir: model predictions
│   ├── demo-model-a/
│   │   ├── oracle_bone_artifacts/
│   │   │   └── results/
│   │   │       ├── oracle_bone_artifacts_000001.json
│   │   │       └── ...
│   │   └── ...
│   └── demo-model-b/
│       └── ...
│
└── evaluate_results/           # ← result_folder: auto-created
    ├── evaluation_table_latex.txt
    ├── evaluation_table.xlsx
    └── evaluation_report.json
```

### 2.1 Dataset scale

| Category | Column | Samples |
|---|---|---:|
| `oracle_bone_artifacts` | Oracle | 300 |
| `bronze_rubbings` | Bronze | 250 |
| `bamboo_wooden_slips` | Slip | 300 |
| `silk_manuscripts` | Silk | 300 |
| `seals` | Seal | 350 |
| `inscription_rubbings` | Stele | 300 |
| `cliff_carvings` | Cliff | 200 |
| `traditional_chinese_book_editions` | Editions | 300 |
| `calligraphys` | Calligraphy | 400 |
| **Total** | | **2,700** |

### 2.2 Ground-truth format

`<gt_dir>/<category>/conv.jsonl` — one JSON per line:

```json
{"image": "oracle_bone_artifacts_000001.png", "human_gt": "貞今夕雨"}
```

Only `image` and `human_gt` are used; other fields are ignored. This release is the clean version — the images themselves are distributed separately, and the evaluator never reads them.

### 2.3 Prediction format

`<root_dir>/<model>/<category>/results/<file_id>.json`

`file_id` is `image` minus its extension, e.g. `oracle_bone_artifacts_000001.png` → `oracle_bone_artifacts_000001.json`. 

```json
{"answer": "<res>貞今夕雨</res>"}
```

## 3. Using Your Own Data

Change three things in `config.yaml`:

```yaml
evaluation_setup:
  selected_apis:                  # ① your model names = dir names under root_dir
    - model-v1
    - model-v2

  paths:
    root_dir: "./infer_results"   # ② prediction root
    gt_dir:   "./Ancient_Bench"   # ③ benchmark root
    result_folder: "evaluate_results"

  selected_data_category:         # delete lines to evaluate a subset
    - oracle_bone_artifacts
    - bronze_rubbings
    - bamboo_wooden_slips
    - silk_manuscripts
    - seals
    - inscription_rubbings
    - cliff_carvings
    - traditional_chinese_book_editions
    - calligraphys

verifier_params:
  ignore_st:    false   # ignore Traditional-vs-Simplified
  ignore_punc:  true    # ignore punctuation
  ignore_space: true    # ignore whitespace
  ignore_case:  false   # ignore letter case
```

---

## 4. Metrics

Both metrics are computed over the **normalized token sequence** (see §5).

**① Edit-distance score**

```
score = 1 - Levenshtein(gt, pred) / max(len(gt), len(pred))
```

**② Character F1**

Multiset intersection over characters (per-character `min` count), then precision / recall / F1. Order-agnostic — only which characters appear, and how many times.

**Overall** = unweighted mean across categories (macro average). Because it is not sample-weighted, every carrier contributes equally regardless of its sample count.

---

## 5. Text Normalization

Scores depend entirely on the normalized text, so this section effectively defines how your model should format its output.

### 5.1 Applied to predictions only

| Step | Behavior |
|---|---|
| `<res>...</res>` extraction | If present, **only the wrapped content is scored** — so it is safe to emit reasoning outside the tag |
| Tag stripping | `<img>` `<page_number>` `<watermark>` `<signature>` — these tags **and their contents** are removed entirely |
| `#` removal | All `#` characters are dropped (markdown headings) |

### 5.2 Applied to both ground truth and predictions

| Step | Behavior |
|---|---|
| `<note>` `<ignore>` | Tags removed, **content kept** |
| Traditional → Simplified | OpenCC `t2s` when `ignore_st: true` |
| Repeat collapsing | Runs of `▢` or `〇` collapse to a single character |
| Punctuation filter | When `ignore_punc: true`, drops Unicode `P*` categories except the allowlist `< > = - ▢ 〇 ~ ～ 、` |
| Whitespace filter | When `ignore_space: true`, all whitespace is dropped |
| Special tokens | `<unrecognizable>` and `<undeciphered>` each count as **one token**, not split into characters |

Everything else is split per character.

> 💡 Because the special tokens count as single units, omitting one undeciphered character costs exactly 1 token — not the length of the tag string.

---


## Citation

If this benchmark helps your research, please cite our paper.

```bibtex
@inproceedings{cheng2026ancientbench,
  title={Ancient-Bench: A Comprehensive Multi-millennial, Multi-medium, and Multi-script Benchmark for Ancient Chinese Artifact Text Recognition},
  author={Cheng, Hiuyi and Xu, Nuo and Zhang, Yuyi and Zheng, Xuhan and Pan, Wei and Zhang, Jing and Peng, Dezhi and Liao, Minghui and Teng, Yihua and Wu, Jihao and Ren, Haoyu and Jin, Lianwen},
  booktitle={Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year={2026},
  url={https://arxiv.org/abs/2608.27169}
}
