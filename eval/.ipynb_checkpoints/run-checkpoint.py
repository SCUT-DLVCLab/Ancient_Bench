import os
import re
import json
import yaml
import logging
import unicodedata
import Levenshtein
import pandas as pd
from tqdm import tqdm
from opencc import OpenCC
from typing import Dict, Any
from collections import Counter


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s")
logger = logging.getLogger("EvalPipeline")
T2S_CONVERTER = OpenCC('t2s') 

def normalized_edit_distance(s1: list, s2: list) -> float:
    dist = Levenshtein.distance(s1, s2)
    max_len = max(len(s1), len(s2))
    return float(dist / max_len) if max_len > 0 else 0.0


def calculate_char_f1(predict: list, target: list) -> float:
    if not predict:
        return 0.0

    pred_counts = Counter(predict)
    gt_counts = Counter(target)

    intersection = 0
    for char, count in pred_counts.items():
        if char in gt_counts:
            intersection += min(count, gt_counts[char])

    if intersection == 0:
        return 0.0

    precision = intersection / len(predict)
    recall = intersection / len(target)

    f1 = 2 * (precision * recall) / (precision + recall)
    return f1


def text_preprocess_for_eval(
    text: str,
    is_predict: bool,
    ignore_space: bool,
    ignore_punc: bool,
    ignore_case: bool,
    ignore_st: bool,
) -> list:
    if not text:
        return []

    if is_predict:
        match = re.search(r"<res>(.*?)</res>", text, flags=re.DOTALL)
        if match:
            text = match.group(1)
        text = text.strip('\n')
        
        tags = ["img", "page_number", "watermark", "signature"]
        for tag in tags:
            text = re.sub(rf"<{tag}>.*?</{tag}>", "", text, flags=re.DOTALL)
            text = text.replace(f"<{tag}>", "")
            text = text.replace(f"</{tag}>", "")
    
        text = text.replace("#", "")

    text = re.sub(r"</?note>|</?ignore>", "", text)

    if ignore_st:
        text = T2S_CONVERTER.convert(text)

    if ignore_case:
        text = text.lower()

    text = re.sub(r"(▢)\1+", r"\1", text)
    text = re.sub(r"(〇)\1+", r"\1", text)

    if ignore_punc:
        keep_chars = {'<', '>', '=', '-', '▢', '〇', '~', '～', '、'}
        text = "".join(
            ch for ch in text
            if ch in keep_chars or not unicodedata.category(ch).startswith('P')
        )

    if ignore_space:
        text = re.sub(r"\s+", "", text)

    special_tokens = ["<unrecognizable>", "<undeciphered>"]
    pattern = re.compile("(" + "|".join(map(re.escape, special_tokens)) + ")")
    parts = pattern.split(text)
    
    tokens = []
    for part in parts:
        if part in special_tokens:
            tokens.append(part)
        else:
            tokens.extend(list(part))
    
    return tokens


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    config = load_config("config.yaml")

    eval_setup = config.get("evaluation_setup", {})
    selected_apis = eval_setup.get("selected_apis", [])
    selected_categories = eval_setup.get("selected_data_category", [])
    paths = eval_setup.get("paths", {})

    root_dir = paths.get("root_dir", "./")
    gt_dir = paths.get("gt_dir", "./gt")
    result_folder = paths.get("result_folder", "./results_output")
    os.makedirs(result_folder, exist_ok=True)

    verifier_params = config["verifier_params"]

    results_matrix = {
        api: {
            cat: {"total_edit_score": 0.0, "total_f1_score": 0.0, "count": 0}
            for cat in selected_categories
        }
        for api in selected_apis
    }

    for category in selected_categories:
        conv_path = os.path.join(gt_dir, category, "conv.jsonl")
        with open(conv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in tqdm(lines):
            gt_item = json.loads(line)
            image_file = gt_item["image"]
            assert isinstance(image_file, str) and image_file != ""

            file_id, _ = os.path.splitext(image_file)
            target = gt_item["human_gt"]

            assert isinstance(target, str) and target != ""
            
            for api in selected_apis:
                predict_path = os.path.join(root_dir, api, category, "results", f"{file_id}.json")
                    
                with open(predict_path, "r", encoding="utf-8") as pf:
                    predict = json.load(pf)["answer"]
                    
                if predict is None:
                    predict = ''
                
                cleaned_predict = text_preprocess_for_eval(predict, is_predict=True, **verifier_params)
                cleaned_target = text_preprocess_for_eval(target, is_predict=False, **verifier_params)
                assert len(cleaned_target) > 0
                edit_score = 1.0 - normalized_edit_distance(cleaned_target, cleaned_predict)
                f1_score = calculate_char_f1(cleaned_predict, cleaned_target)
                    
                results_matrix[api][category]["total_edit_score"] += edit_score
                results_matrix[api][category]["total_f1_score"] += f1_score
                results_matrix[api][category]["count"] += 1

    
    category_display_map = {
        "oracle_bone_artifacts": "Oracle",
        "bronze_rubbings": "Bronze",
        "bamboo_wooden_slips": "Slip",
        "silk_manuscripts": "Silk",
        "seals": "Seal",
        "inscription_rubbings": "Stele",
        "cliff_carvings": "Cliff",
        "traditional_chinese_book_editions": "Editions",
        "calligraphys": "Calligraphy"
    }

    latex_lines = []
    excel_rows = []

    for api in selected_apis:
        row_values = []
        total_edit = 0.0
        total_f1 = 0.0
        cat_count = 0

        for category in selected_categories:
            stats = results_matrix[api][category]
            count = stats["count"]

            avg_edit = stats["total_edit_score"] / count if count > 0 else 0.0
            avg_f1 = stats["total_f1_score"] / count if count > 0 else 0.0

            total_edit += avg_edit
            total_f1 += avg_f1
            cat_count += 1

            row_values.append(f"{avg_edit:.2f} / {avg_f1:.2f}")

        overall_edit = total_edit / cat_count if cat_count > 0 else 0.0
        overall_f1 = total_f1 / cat_count if cat_count > 0 else 0.0

        row_values.append(f"{overall_edit:.2f} / {overall_f1:.2f}")

        latex_line = f"{api} & " + " & ".join(row_values) + " \\\\"
        latex_lines.append(latex_line)

        excel_row = {"Model": api}
        for idx, category in enumerate(selected_categories):
            display_name = category_display_map.get(category, category)
            excel_row[display_name] = row_values[idx]

        excel_row["Overall"] = row_values[-1]
        excel_rows.append(excel_row)

    latex_path = os.path.join(result_folder, "evaluation_table_latex.txt")
    with open(latex_path, "w", encoding="utf-8") as f:
        
        header_categories = [
            category_display_map.get(cat, cat) for cat in selected_categories
        ]
        header_line = "Model & " + " & ".join(header_categories) + " & Overall \\\\"
        f.write(header_line + "\n")

        for line in latex_lines:
            f.write(line + "\n")

    df_excel = pd.DataFrame(excel_rows)
    ordered_columns = ["Model"] + \
                      [category_display_map.get(cat, cat) for cat in selected_categories] + \
                      ["Overall"]
    df_excel = df_excel[ordered_columns]

    xlsx_path = os.path.join(result_folder, "evaluation_table.xlsx")
    df_excel.to_excel(xlsx_path, index=False)

    json_path = os.path.join(result_folder, "evaluation_report.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(results_matrix, jf, indent=4, ensure_ascii=False)

    logger.info("✅ 评测完成")
    logger.info(f"LaTeX: {latex_path}")
    logger.info(f"Excel: {xlsx_path}")
    logger.info(f"JSON : {json_path}")


if __name__ == "__main__":
    main()