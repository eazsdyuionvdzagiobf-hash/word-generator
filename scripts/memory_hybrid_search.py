#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import lancedb

WORKSPACE = Path('/Users/huangjunjie/.openclaw/workspace')
DB_URI = WORKSPACE / 'data' / 'memory-lancedb'
TABLE = 'memory_text'


def lance_hits(query: str, limit: int) -> list[dict]:
    db = lancedb.connect(str(DB_URI))
    if TABLE not in db.table_names():
        return []
    table = db.open_table(TABLE)
    q = query.lower().replace("'", "''")
    where = f"contains(text_lower, '{q}') or contains(summary, '{q}') or contains(title, '{q}')"
    rows = table.search().where(where).limit(limit).to_list()
    out = []
    for row in rows:
        out.append({
            'engine': 'lancedb',
            'source_file': row['source_file'],
            'title': row['title'],
            'summary': row.get('summary', ''),
            'memory_layer': row.get('memory_layer', ''),
            'importance': row.get('importance', 0),
        })
    return out


def qmd_hits(query: str, limit: int) -> list[dict]:
    cmd = ['qmd', 'search', query, '--json', '-n', str(limit)]
    try:
        proc = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True, timeout=30, check=True)
    except Exception:
        return []
    try:
        data = json.loads(proc.stdout)
    except Exception:
        return []
    out = []
    for item in data if isinstance(data, list) else []:
        out.append({
            'engine': 'qmd',
            'source_file': item.get('path', ''),
            'title': item.get('title', item.get('path', '')),
            'summary': item.get('snippet', ''),
            'memory_layer': '',
            'importance': 0,
        })
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description='Hybrid memory search across QMD and LanceDB.')
    parser.add_argument('query')
    parser.add_argument('--limit', type=int, default=5)
    args = parser.parse_args()

    hits = []
    seen = set()
    for item in lance_hits(args.query, args.limit) + qmd_hits(args.query, args.limit):
        key = (item['engine'], item['source_file'], item['summary'])
        if key in seen:
            continue
        seen.add(key)
        hits.append(item)

    print(f'Hybrid matches: {len(hits[:args.limit])}')
    for i, row in enumerate(hits[: args.limit], 1):
        print(f'[{i}] [{row["engine"]}] {row["source_file"]} | {row["title"]}')
        if row['memory_layer']:
            print(f'    layer={row["memory_layer"]} importance={row["importance"]}')
        if row['summary']:
            print(f'    {row["summary"][:220].replace(chr(10), " ")}')


if __name__ == '__main__':
    main()
