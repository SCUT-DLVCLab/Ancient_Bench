# Ancient-Bench 评测工具

<p align="center">
  <a href="README.md">English</a> | <b>简体中文</b>
</p>

Ancient-Bench 基准测试的评测脚本，覆盖 **9 类文字载体**：甲骨、金文拓片、简牍、帛书、玺印、碑刻拓片、摩崖石刻、古籍版本、书法。

仓库自带**真实 benchmark 标注 + 两个示例模型的预测**（9 类共 2700 条），克隆后 `python run.py` 即可跑通完整流程。

---

## 1. 快速开始

```bash
pip install pyyaml python-Levenshtein pandas tqdm openpyxl opencc-python-reimplemented

python run.py
```

输出：

```
[INFO] ✅ 评测完成
[INFO] LaTeX: evaluate_results/evaluation_table_latex.txt
[INFO] Excel: evaluate_results/evaluation_table.xlsx
[INFO] JSON : evaluate_results/evaluation_report.json
```

样例结果（`evaluation_table_latex.txt`）：

```
Model & Oracle & Bronze & Slip & Silk & Seal & Stele & Cliff & Editions & Calligraphy & Overall \\
demo-model-a & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 & 1.00 / 1.00 \\
demo-model-b & 0.92 / 0.95 & 0.89 / 0.94 & 0.86 / 0.92 & 0.84 / 0.91 & 0.86 / 0.92 & 0.81 / 0.90 & 0.88 / 0.93 & 0.77 / 0.87 & 0.81 / 0.90 & 0.85 / 0.92 \\
```

---

## 2. 目录结构

```
.
├── run.py                      # 评测脚本
├── config.yaml                 # 配置（唯一需要改的文件）
│
├── Ancient_Bench/              # ← gt_dir：标注数据
│   ├── oracle_bone_artifacts/
│   │   └── conv.jsonl
│   ├── bronze_rubbings/
│   │   └── conv.jsonl
│   └── ...                     # 共 9 个类别
│
├── infer_results/              # ← root_dir：模型推理结果
│   ├── demo-model-a/
│   │   ├── oracle_bone_artifacts/
│   │   │   └── results/
│   │   │       ├── oracle_bone_artifacts_000001.json
│   │   │       └── ...
│   │   └── ...
│   └── demo-model-b/
│       └── ...
│
└── evaluate_results/           # ← result_folder：自动生成
    ├── evaluation_table_latex.txt
    ├── evaluation_table.xlsx
    └── evaluation_report.json
```

### 2.1 数据规模

| 类别 | 表头 | 条数 |
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
| **合计** | | **2700** |

### 2.2 GT 格式

`<gt_dir>/<category>/conv.jsonl` —— 每行一个 JSON：

```json
{"image": "oracle_bone_artifacts_000001.png", "human_gt": "貞今夕雨"}
```

只需要 `image` 和 `human_gt` 两个字段，其余字段会被忽略。本次发布的是纯净版，图片单独分发，评测脚本本身不读图。

### 2.3 预测格式

`<root_dir>/<model>/<category>/results/<file_id>.json`

其中 `file_id` 是 `image` 去掉扩展名，例如 `oracle_bone_artifacts_000001.png` → `oracle_bone_artifacts_000001.json`。

```json
{"answer": "<res>貞今夕雨</res>"}
```

---

## 3. 换成你自己的数据

只改 `config.yaml` 三处：

```yaml
evaluation_setup:
  selected_apis:                  # ① 你的模型名 = root_dir 下的目录名
    - model-v1
    - model-v2

  paths:
    root_dir: "./infer_results"   # ② 推理结果根目录
    gt_dir:   "./Ancient_Bench"   # ③ benchmark 根目录
    result_folder: "evaluate_results"

  selected_data_category:         # 想只跑部分类别就删掉几行
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
  ignore_st:    false   # 忽略简繁差异
  ignore_punc:  true    # 忽略标点
  ignore_space: true    # 忽略空白
  ignore_case:  false   # 忽略英文大小写
```

---

## 4. 评测指标

两个指标都在**归一化后的 token 序列**上计算（归一化规则见第 5 节）。

**① 编辑距离得分**

```
score = 1 - Levenshtein(gt, pred) / max(len(gt), len(pred))
```

**② 字符 F1**

按字符多重集合取交集（`Counter` 的 `min` 计数），再算 precision / recall / F1。不考虑顺序，只考虑字符是否出现及出现次数。

**总分（Overall）** = 各类别得分的算术平均（宏平均）。因为不按样本数加权，所以每个载体的权重相同，与其条数无关。

---

## 5. 文本归一化细节

分数完全取决于归一化后的文本，所以这一节实际上决定了你的模型该怎么输出。

### 5.1 只作用于预测的处理

| 步骤 | 行为 |
|---|---|
| `<res>...</res>` 抽取 | 有该标签则**只取标签内内容**参与打分，因此标签外可以安全输出思维链 |
| 标签剥离 | `<img>` `<page_number>` `<watermark>` `<signature>` —— 这些标签**连同其内容**整段删除 |
| `#` 删除 | 所有 `#` 直接去掉（Markdown 标题符） |

### 5.2 GT 与预测都做的处理

| 步骤 | 行为 |
|---|---|
| `<note>` `<ignore>` | 只删标签本身，**保留内容** |
| 简繁转换 | `ignore_st: true` 时用 OpenCC `t2s` 转简体 |
| 重复符号折叠 | 连续的 `▢` 或 `〇` 折叠成一个 |
| 标点过滤 | `ignore_punc: true` 时删除 Unicode `P*` 类，但保留白名单 `< > = - ▢ 〇 ~ ～ 、` |
| 空白过滤 | `ignore_space: true` 时删除所有空白 |
| 特殊 token | `<unrecognizable>` 和 `<undeciphered>` 各算**一个 token**，不拆成单字 |

其余字符逐字拆分。

> 💡 因为特殊 token 整体计一个单位，模型漏写一个未释字只扣 1 个 token，而不是按标签字符串的长度扣分。

---

## 引用

如果本 benchmark 对你的研究有帮助，请引用我们的论文。

```bibtex
@article{ancientbench,
  title  = {Ancient-Bench: A Benchmark for Ancient Chinese OCR},
  author = {TODO},
  year   = {2026}
}
```
