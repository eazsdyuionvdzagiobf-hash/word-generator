#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import lancedb

WORKSPACE = Path('/Users/huangjunjie/.openclaw/workspace')
DB_URI = WORKSPACE / 'data' / 'memory-lancedb'
TABLE = 'memory_text'


def score_row(row: dict, query: str) -> float:
    q = query.lower()
    text = row['text_lower']
    summary = row.get('summary', '').lower()
    title = row.get('title', '').lower()
    score = 0.0
    if q in title:
        score += 0.45
    if q in summary:
        score += 0.35
    if q in text:
        score += 0.25
    score += float(row.get('importance', 0.0)) * 0.20
    score += float(row.get('confidence', 0.0)) * 0.10
    if row.get('memory_layer') == 'semantic':
        score += 0.05
    return score


def main() -> None:
    parser = argparse.ArgumentParser(description='Search mirrored memory records in LanceDB (text/metadata only).')
    parser.add_argument('query', help='substring to search in memory text')
    parser.add_argument('--limit', type=int, default=5)
    parser.add_argument('--layer', choices=['semantic', 'episodic', 'inbox'])
    args = parser.parse_args()

    db = lancedb.connect(str(DB_URI))
    if TABLE not in db.table_names():
        raise SystemExit('memory_text table not found. Run scripts/lancedb_memory_sync.py first.')
    table = db.open_table(TABLE)
    q = args.query.lower().replace("'", "''")
    clauses = [f"contains(text_lower, '{q}') or contains(summary, '{q}') or contains(title, '{q}')"]
    if args.layer:
        clauses.append(f"memory_layer = '{args.layer}'")
    where = ' and '.join(f'({c})' for c in clauses)
    rows = table.search().where(where).limit(max(args.limit * 3, 10)).to_list()
    ranked = sorted(rows, key=lambda r: score_row(r, args.query), reverse=True)[: args.limit]
    print(f'Matches: {len(ranked)}')
    for i, row in enumerate(ranked, 1):
        preview = row['summary'] or row['text'].replace('\n', ' ')[:180]
        print(f'[{i}] {row["source_file"]} | {row["title"]}')
        print(f'    layer={row["memory_layer"]} status={row["status"]} importance={row["importance"]:.2f} confidence={row["confidence"]:.2f}')
        print(f'    tags={row.get("tags", "")}')
        print(f'    {preview}')


if __name__ == '__main__':
    main()
