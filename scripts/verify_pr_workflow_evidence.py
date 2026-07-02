#!/usr/bin/env python3
"""Verify that a PR workflow comment task has attached evidence before marking done.

Checks the issue comments for a verifiable artifact (URL, comment ID, commit SHA, or diff).
Returns a non-zero exit code if evidence is missing.
"""
import json
import re
import sys
import urllib.request
from urllib.error import HTTPError

EVIDENCE_PATTERNS = [
    r'https?://github\.com/[^\s]+/pull/\d+#issuecomment-\d+',  # PR comment URL
    r'https?://github\.com/[^\s]+/commit/[0-9a-f]{7,40}',      # commit URL
    r'https?://github\.com/[^\s]+/compare/[^\s]+',                # diff URL
    r'#issuecomment-\d+',                                        # bare comment ID
    r'comment[-_]?id[:\s=]+\d+',                                  # comment ID forms
    r'commit[-_]?sha[:\s=]+[0-9a-f]{7,40}',                       # commit SHA forms
]


def has_evidence(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in EVIDENCE_PATTERNS)


def fetch_comments(base_url: str, token: str) -> list:
    req = urllib.request.Request(
        base_url,
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def main():
    if len(sys.argv) < 2:
        print('Usage: verify_pr_workflow_evidence.py <issue_comments_json_url> [token]')
        sys.exit(2)

    comments_url = sys.argv[1]
    token = sys.argv[2] if len(sys.argv) > 2 else ''

    try:
        comments = fetch_comments(comments_url, token)
    except HTTPError as e:
        print(f'FAIL: unable to fetch comments ({e.code})')
        sys.exit(1)
    except Exception as e:
        print(f'FAIL: unable to fetch comments ({e})')
        sys.exit(1)

    if not isinstance(comments, list):
        print('FAIL: comments payload is not a list')
        sys.exit(1)

    all_text = '\n'.join(c.get('body', '') for c in comments)
    if has_evidence(all_text):
        print('PASS: evidence artifact found in issue comments')
        sys.exit(0)
    else:
        print('FAIL: no verifiable evidence artifact found in issue comments')
        sys.exit(1)


if __name__ == '__main__':
    main()
