#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import lancedb

WORKSPACE = Path('/Users/huangjunjie/.openclaw/workspace')
DB_URI = WORKSPACE / 'data' / 'memory-lancedb'
TABLE = 'memory_text'


@dataclass
class Record:
    id: str
    source_file: str
    title: str
    memory_type: str
    memory_layer: str
    status: str
    summary: str
    tags: str
    importance: float
    confidence: float
    text: str
    text_lower: str
    line_count: int
    created_at: str
    updated_at: str
    last_seen_at: str
    checksum: str


def iter_memory_files() -> Iterable[Path]:
    files = []
    long_term = WORKSPACE / 'MEMORY.md'
    if long_term.exists():
        files.append(long_term)
    mem_dir = WORKSPACE / 'memory'
    if mem_dir.exists():
        files.extend(sorted(mem_dir.glob('*.md')))
    return files


def normalize_text(text: str) -> str:
    text = text.replace('\r\n', '\n').strip()
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def title_from_text(path: Path, text: str) -> str:
    for line in text.splitlines():
        if line.startswith('#'):
            return line.lstrip('#').strip() or path.name
    return path.name


def memory_type_for(path: Path) -> str:
    if path.name == 'MEMORY.md':
        return 'long_term'
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}\.md', path.name):
        return 'daily'
    return 'note'


def layer_for(memory_type: str) -> str:
    if memory_type == 'long_term':
        return 'semantic'
    if memory_type == 'daily':
        return 'episodic'
    return 'inbox'


def status_for(memory_type: str) -> str:
    return 'confirmed' if memory_type == 'long_term' else 'candidate'


def importance_for(memory_type: str, text: str) -> float:
    score = 0.55 if memory_type == 'long_term' else 0.35
    hints = ['记住', '偏好', '不要', '必须', '长期', 'important', 'always', 'never']
    if any(h in text.lower() for h in hints):
        score += 0.2
    if '## Identity' in text or '## Notes' in text:
        score += 0.15
    return min(score, 1.0)


def confidence_for(memory_type: str) -> float:
    return 0.95 if memory_type == 'long_term' else 0.7


def extract_tags(path: Path, text: str) -> list[str]:
    tags = set()
    base = path.stem.lower()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', base):
        tags.add('daily-note')
    if path.name == 'MEMORY.md':
        tags.add('long-term')
    keyword_map = {
        'telegram': 'telegram',
        'qmd': 'qmd',
        'lancedb': 'lancedb',
        'memory': 'memory',
        'embedding': 'embedding',
        'openclaw': 'openclaw',
    }
    low = text.lower()
    for key, tag in keyword_map.items():
        if key in low:
            tags.add(tag)
    return sorted(tags)


def summarize(text: str) -> str:
    lines = [ln.strip('- ').strip() for ln in text.splitlines() if ln.strip()]
    body = [ln for ln in lines if not ln.startswith('#')]
    summary = ' | '.join(body[:3]) if body else (lines[0] if lines else '')
    return summary[:280]


def make_record(path: Path) -> Record:
    raw = path.read_text(encoding='utf-8', errors='ignore')
    text = normalize_text(raw)
    rel = path.relative_to(WORKSPACE).as_posix()
    checksum = hashlib.sha256(text.encode('utf-8')).hexdigest()
    stat = path.stat()
    created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat()
    updated = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    now = datetime.now(timezone.utc).isoformat()
    memory_type = memory_type_for(path)
    rec_id = hashlib.sha256(f'{rel}:{checksum}'.encode('utf-8')).hexdigest()[:24]
    tags = extract_tags(path, text)
    return Record(
        id=rec_id,
        source_file=rel,
        title=title_from_text(path, text),
        memory_type=memory_type,
        memory_layer=layer_for(memory_type),
        status=status_for(memory_type),
        summary=summarize(text),
        tags=','.join(tags),
        importance=importance_for(memory_type, text),
        confidence=confidence_for(memory_type),
        text=text,
        text_lower=text.lower(),
        line_count=text.count('\n') + 1 if text else 0,
        created_at=created,
        updated_at=updated,
        last_seen_at=now,
        checksum=checksum,
    )


def main() -> None:
    DB_URI.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(DB_URI))
    rows = [asdict(r) for r in map(make_record, iter_memory_files())]
    if not rows:
        print('No memory files found.')
        return
    existing = set(db.table_names())
    if TABLE in existing:
        db.drop_table(TABLE)
    tbl = db.create_table(TABLE, data=rows)
    print(f'DB: {DB_URI}')
    print(f'Table: {TABLE}')
    print(f'Rows: {tbl.count_rows()}')
    print('Files:')
    for row in rows:
        print(f"- {row['source_file']} | layer={row['memory_layer']} | status={row['status']} | importance={row['importance']:.2f}")


if __name__ == '__main__':
    main()
