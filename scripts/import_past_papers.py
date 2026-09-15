"""Copy user-provided originals, hash-verify, and build an auditable catalogue.

Does not execute or follow instructions in imported documents. Re-running is safe;
an existing destination with different bytes is rejected, never overwritten.
Requires pypdfium2 and mutagen; metadata checks do not certify full decoding.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

import pypdfium2
from mutagen.mp3 import MP3

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'materials/past_papers'
SOURCES = {'N1': 'N1真题', 'N2': 'N2真题', 'N3': 'N3真题',
           'N4': 'N4历年真题', 'N5': 'N5历年真题'}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def session_for(relative):
    text = relative.as_posix()
    if '1991-2009' in text:
        return 'pre-2010'
    if '2010-2011' in text:
        return '2010-2011-unspecified'
    m = re.search(r'(20\d{2})[年. -](0?[1-9]|1[0-2])(?:月|/|[^0-9]|$)', text)
    if m:
        return f'{m[1]}-{int(m[2]):02d}'
    m = re.search(r'(?:^|/)(25)年(\d{1,2})月', text)
    if m:
        return f'2025-{int(m[2]):02d}'
    m = re.search(r'20\d{2}', text)
    return m[0] + '-unspecified' if m else 'supplement'


def roles_for(path):
    name = path.name
    if path.suffix.lower() in ('.mp3', '.wav', '.m4a'):
        return ['audio']
    roles = []
    if '答题卡' in name or '答题纸' in name:
        return ['answer_sheet']
    if '计算' in name:
        return ['unverified_scoring_reference']
    if '答案' in name or '解析' in name:
        roles.append('answer_or_explanation')
    if '原文' in name:
        roles.append('listening_script')
    if '译文' in name:
        roles.append('translation')
    if (not roles or any(x in name for x in ('真题+', '真题（含', '试卷'))):
        roles.append('paper_candidate')
    return roles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, default=Path('D:/video'))
    args = parser.parse_args()
    files = []
    for level, folder in SOURCES.items():
        source = args.source_root / folder
        if not source.is_dir():
            raise FileNotFoundError(source)
        for path in sorted(source.rglob('*')):
            if not path.is_file():
                continue
            rel = path.relative_to(source)
            dest = BASE / 'raw' / level / rel
            sha = digest(path)
            if dest.exists():
                if digest(dest) != sha:
                    raise RuntimeError(f'Destination differs: {dest}')
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
                assert digest(dest) == sha, str(dest)
            record = dict(level=level, session=session_for(rel),
                          source=str(path), path=dest.relative_to(ROOT).as_posix(),
                          bytes=path.stat().st_size, sha256=sha,
                          roles_inferred_from_name=roles_for(path),
                          provenance='user_provided_unverified_past_paper',
                          content_pairing='not_yet_checked',
                          student_exposure='not_assessed', copy_verified=True)
            if level == 'N1':
                record['validation'] = 'hash_only_archived_no_curriculum_review'
            elif path.suffix.lower() == '.pdf':
                try:
                    pdf = pypdfium2.PdfDocument(dest)
                    record['pages'] = len(pdf)
                    pdf.close()
                    record['validation'] = 'pdf_parses_not_full_visual_review'
                except Exception as exc:
                    record['validation'] = 'pdf_parse_failed'
                    record['error'] = str(exc)
            elif path.suffix.lower() in ('.mp3', '.wav', '.m4a'):
                probe = shutil.which('ffprobe')
                if probe:
                    result = subprocess.run([probe, '-v', 'error', '-show_entries',
                        'format=duration:stream=codec_name,sample_rate,channels',
                        '-of', 'json', str(dest)], capture_output=True, text=True)
                    record['validation'] = 'audio_metadata_probed' if result.returncode == 0 else 'audio_probe_failed'
                    if result.returncode == 0:
                        record['audio_metadata'] = json.loads(result.stdout)
                else:
                    try:
                        info = MP3(dest).info
                        record['audio_metadata'] = dict(duration_seconds=round(info.length, 3),
                            sample_rate=info.sample_rate, channels=info.channels, bitrate=info.bitrate)
                        record['validation'] = 'audio_metadata_probed_not_full_decode'
                    except Exception as exc:
                        record['validation'] = 'audio_probe_failed'
                        record['error'] = str(exc)
            else:
                record['validation'] = 'hash_only_not_opened'
            files.append(record)
        print(level, sum(x['level'] == level for x in files), 'copied and verified', flush=True)
    groups = collections.defaultdict(list)
    hashes = collections.defaultdict(list)
    for item in files:
        groups[(item['level'], item['session'])].append(item)
        hashes[item['sha256']].append(item['path'])
    sessions = []
    lines = ['# 用户题库清单（2026-09-16）', '',
             '> 文件名场次／角色为初筛，解析成功不等于官方来源认证或整卷完整。逐题配套以 QA_NOTES.md 为准。N1仅归档。', '',
             '|等级|文件数|字节数|', '|---|---:|---:|']
    for level in SOURCES:
        items = [x for x in files if x['level'] == level]
        lines.append(f'|{level}|{len(items)}|{sum(x["bytes"] for x in items):,}|')
    lines += ['', '|等级／场次|文件数|题卷候选|答案／解析|音频|原文|用途|', '|---|---:|---:|---:|---:|---:|---|']
    for (level, session), items in sorted(groups.items(), key=lambda kv: (kv[0][0], -int(re.sub(r'\D', '', kv[0][1]) or 0))):
        counts = collections.Counter(r for x in items for r in x['roles_inferred_from_name'])
        sessions.append(dict(level=level, session=session, file_count=len(items),
                             role_counts=dict(counts), paths=[x['path'] for x in items],
                             ready_for_full_mock=False,
                             status='archive_only' if level == 'N1' else 'inventory_only_requires_question_level_QA'))
        purpose = '归档不教学' if level == 'N1' else '待逐题核对'
        if session == 'pre-2010': purpose = '旧制参考，不作现行模拟'
        lines.append(f'|{level} {session}|{len(items)}|{counts["paper_candidate"]}|{counts["answer_or_explanation"]}|{counts["audio"]}|{counts["listening_script"]}|{purpose}|')
    duplicates = [v for v in hashes.values() if len(v) > 1]
    data = dict(imported_on='2026-09-16', scope='N1 archive; N2 primary; N3-N5 targeted bridges',
                total_files=len(files), total_bytes=sum(x['bytes'] for x in files),
                files=files, sessions=sessions, exact_duplicate_groups=duplicates)
    (BASE / 'manifest.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines += ['', f'完全相同文件组：{len(duplicates)}；保留原目录避免丢失来源，LFS按内容寻址复用。',
              '', '完整路径、SHA-256、页数、音频元数据、重复项见 manifest.json。仅有答案／原文的场次不能作完整试卷。']
    (BASE / 'INVENTORY.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({k:data[k] for k in ('total_files','total_bytes')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
