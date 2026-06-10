import json
import os
from pathlib import Path

def load_json_file(filepath):
    """加载单个 JSON 文件，支持对象或数组根节点"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 如果根节点是对象且包含 results，则提取 results 列表
    if isinstance(data, dict) and 'results' in data:
        return data['results']
    # 如果根节点是列表，直接返回
    elif isinstance(data, list):
        return data
    else:
        return [data]

def normalize_record(record):
    """将记录统一为可比较的字典格式，处理字段名差异"""
    normalized = {}
    # 统一用户ID字段
    if 'uid' in record:
        normalized['uid'] = record['uid']
    elif 'user_id' in record:
        normalized['uid'] = record['user_id']
    elif 'trace_id' in record:
        normalized['trace_id'] = record['trace_id']

    # 统一时间字段
    if 'time' in record:
        normalized['time'] = record['time']
    elif 'timestamp' in record:
        normalized['time'] = record['timestamp']

    # 统一行为/类型字段
    if 'action' in record:
        normalized['action'] = record['action']
    elif 'type' in record:
        normalized['action'] = record['type']
    elif 'tool' in record:
        normalized['tool'] = record['tool']

    # 统一内容字段
    if 'content' in record:
        normalized['content'] = record['content']
    elif 'text' in record:
        normalized['content'] = record['text']
    elif 'output' in record:
        normalized['content'] = record['output']

    # 保留其他字段
    for k, v in record.items():
        if k not in normalized and k not in ('uid', 'user_id', 'time', 'timestamp',
                                               'action', 'type', 'tool',
                                               'content', 'text', 'output'):
            normalized[k] = v
    return normalized

def record_key(record):
    """生成用于去重的键：基于所有值的元组"""
    normalized = normalize_record(record)
    # 按key排序后取values元组，确保相同内容生成相同key
    return tuple(sorted((k, str(v)) for k, v in normalized.items()))

def main():
    input_dir = Path('student-camp-data/raw/d2')
    output_file = Path('merged.json')

    all_records = []
    seen_keys = set()

    # 遍历目录下所有 .json 文件
    for filepath in sorted(input_dir.glob('*.json')):
        print(f"正在读取: {filepath}")
        records = load_json_file(filepath)
        for rec in records:
            key = record_key(rec)
            if key not in seen_keys:
                seen_keys.add(key)
                all_records.append(rec)
            else:
                print(f"  去重记录: {rec}")

    # 写入合并后的文件，每行一个 JSON 对象（JSON Lines 格式）
    with open(output_file, 'w', encoding='utf-8') as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')

    print(f"\n合并完成，共 {len(all_records)} 条唯一记录，输出到 {output_file}")

    # 验证行数
    with open(output_file, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    print(f"文件行数: {line_count}")
    assert line_count >= 8, f"行数不足: {line_count} < 8"
    print("行数验证通过 (>= 8)")

if __name__ == '__main__':
    main()
