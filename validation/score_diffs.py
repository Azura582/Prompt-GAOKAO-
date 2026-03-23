
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List


def compute_stats(p: Path) -> Dict[str, Any]:
    if not p.exists():
        raise FileNotFoundError(f"输入文件不存在: {p}")

    obj = json.loads(p.read_text(encoding='utf-8'))
    if isinstance(obj, dict) and 'questions' in obj:
        qs = obj['questions']
    elif isinstance(obj, list):
        qs = obj
    else:
        raise ValueError('无法识别输入 JSON 结构，期望为 {"questions": [...]} 或者 一个题目列表')

    diffs: List[float] = []
    abs_diffs: List[float] = []
    sq_diffs: List[float] = []
    n_missing = 0
    n_total = len(qs)
    n_exact = 0

    for q in qs:
        # 支持 teacher_score 或 teacher_score 字段可能为字符串或数值
        ts = q.get('teacher_score')
        hs = q.get('human_score')
        if ts is None or hs is None:
            n_missing += 1
            continue
        try:
            tsv = float(ts)
            hsv = float(hs)
        except Exception:
            n_missing += 1
            continue

        d = hsv - tsv
        diffs.append(d)
        abs_diffs.append(abs(d))
        sq_diffs.append(d*d)
        if d == 0:
            n_exact += 1

    n_valid = len(diffs)
    if n_valid == 0:
        raise ValueError('没有有效的 (human_score, teacher_score) 对可计算')

    mean_diff = sum(diffs)/n_valid
    mae = sum(abs_diffs)/n_valid
    rmse = math.sqrt(sum(sq_diffs)/n_valid)
    max_abs = max(abs_diffs)
    exact_rate = n_exact / n_valid
    within_0_5 = sum(1 for v in abs_diffs if v <= 0.5) / n_valid
    within_1_0 = sum(1 for v in abs_diffs if v <= 1.0) / n_valid

    stats = {
        'n_total': n_total,
        'n_valid_pairs': n_valid,
        'n_missing_or_invalid': n_missing,
        'mean_diff': mean_diff,
        'mae': mae,
        'rmse': rmse,
        'max_abs_error': max_abs,
        'exact_match_rate': exact_rate,
        'within_0.5': within_0_5,
        'within_1.0': within_1_0,
    }
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', '-i', default='validation.json', help='合并题目 JSON 文件路径')
    ap.add_argument('--output', '-o', default=None, help='可选：将统计结果写入 JSON 文件')
    ap.add_argument('--pretty', action='store_true', help='如果写入文件，是否使用缩进格式')
    args = ap.parse_args()

    input_path = Path(args.input)

    stats = compute_stats(input_path)

    # 打印到 stdout
    print('\n=== teacher_vs_human score differences ===')
    print(f"total_questions: {stats['n_total']}")
    print(f"valid_pairs: {stats['n_valid_pairs']}")
    print(f"missing_or_invalid_pairs: {stats['n_missing_or_invalid']}")
    print(f"mean_diff (human - teacher): {stats['mean_diff']:.6f}")
    print(f"MAE: {stats['mae']:.6f}")
    print(f"RMSE: {stats['rmse']:.6f}")

    if args.output:
        outp = Path(args.output)
        out_obj = {
            'input': str(input_path),
            'stats': stats,
        }
        if args.pretty:
            outp.write_text(json.dumps(out_obj, ensure_ascii=False, indent=2), encoding='utf-8')
        else:
            outp.write_text(json.dumps(out_obj, ensure_ascii=False), encoding='utf-8')
        print(f'已写统计结果到: {outp}')

if __name__ == '__main__':
    main()
