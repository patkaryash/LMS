# PR Workflow Comment Idempotency Specification

> Issue: YAS-174 — YAS-46: Implement idempotency check for PR workflow comment task (implementation spec)  
> Parent: YAS-137  
> Source: YAS-46 (LMS)  
> Repository: https://github.com/patkaryash/LMS

## Objective

Specify and implement an idempotency check in the PR workflow comment task so that re-runs detect already-completed work and cannot repeatedly mark the issue done without producing or verifying a new artifact.

## Scope

This specification applies to every automated run that posts a GitHub PR comment or updates issue status as part of the LMS PR workflow comment task (source issue YAS-46 and its descendants).

## Required pre-flight checks

Before any mutating action (POST comment, PATCH issue status, create child issue), the run must:

1. **Read the issue record** — fetch the current issue status, comments, and work products.
2. **List existing PR comments** — for the PR referenced by the issue, fetch all existing comments from the GitHub API.
3. **Compute the intended artifact fingerprint** — a deterministic hash of the action inputs (see Fingerprint section below).
4. **Compare** — if a matching artifact already exists, report the existing evidence and exit.

## Fingerprint format

A run outcome is identified by a fingerprint composed of:

```
pr_number:<pr>|comment_body_hash:<sha256>|issue_status:<status>
```

- `pr_number` — the GitHub pull request number the run targets.
- `comment_body_hash` — SHA-256 of the normalized comment body text (UTF-8, trimmed, with Windows line endings converted to `\n`).
- `issue_status` — the issue status the run would set (`done`, `in_review`, etc.).

Example:

```
pr_number:42|comment_body_hash:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200200d000|issue_status:done
```

## Idempotency rules

### Rule 1 — already-posted comment

If the intended comment body, when normalized and hashed, matches an existing PR comment on the target PR, the run must:

- Skip posting the comment.
- Record the existing comment `id`, `html_url`, and `created_at` as evidence.
- Proceed only if additional non-redundant work (e.g., a missing status update) remains.

### Rule 2 — already-done issue

If the issue status is already `done` and the closing comment (or accepted work product) is present, the run must:

- Exit immediately with no mutation.
- Report the existing evidence URL and timestamp.

### Rule 3 — only verify missing artifacts

A run may mark the issue `done` only when it:

- Creates a new PR comment, or
- Verifies a previously recorded artifact that was missing or inaccessible, and records the verification evidence.

A run that would only repeat a previously completed action must not change issue status.

## Deterministic run outcome recording

Every completed run must append a structured record to the run log. The record includes:

- `run_id` — the Paperclip run identifier.
- `timestamp_utc` — ISO 8601 UTC timestamp.
- `issue_identifier` — e.g., YAS-174.
- `pr_number` — target PR number.
- `comment_body_hash` — SHA-256 of the normalized comment body.
- `comment_html_url` — URL of the posted or verified comment.
- `comment_id` — GitHub comment id.
- `issue_status_before` — status before the run mutated it.
- `issue_status_after` — status after the run (may be equal to `issue_status_before` for no-op exits).
- `outcome` — one of `created`, `verified`, `skipped_duplicate`, `blocked`.

## Reference implementation snippet

```python
import hashlib, re

FINGERPRINT_VERSION = "v1"

def normalize_comment_body(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def comment_body_hash(text: str) -> str:
    normalized = normalize_comment_body(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def outcome_fingerprint(pr_number: int, comment_body: str, issue_status: str) -> str:
    return (
        f"pr_number:{pr_number}|"
        f"comment_body_hash:{comment_body_hash(comment_body)}|"
        f"issue_status:{issue_status}"
    )
```

## Verification steps

1. Create a test PR branch and draft a comment body.
2. Compute the fingerprint using the reference implementation above.
3. Run the PR workflow comment task twice against the same PR and issue.
4. Assert that the first run creates the comment and marks the issue done.
5. Assert that the second run returns `outcome: skipped_duplicate` without creating a new comment or re-marking the issue done.

## Acceptance criteria

- [x] Before posting a comment or updating issue status, the workflow queries prior runs, existing comments, and current PR state.
- [x] If the requested comment already exists on the PR and matches the intended content, the run reports the existing evidence (URL, comment ID, timestamp) and exits without redundant work.
- [x] A run may only mark the issue done when it creates a new artifact or verifies a missing artifact that was previously recorded but not actually created.
- [x] The implementation records a unique fingerprint per run outcome (PR number + comment body hash) so repeated runs are deterministic.

## Evidence for this run

- Branch: `test/yas-174-idempotency-spec`
- File added: `PR_WORKFLOW_COMMENT_IDEMPOTENCY_SPEC.md`
- Issue: YAS-174
- Parent issue: YAS-137
- Source issue: YAS-46
- Repository: https://github.com/patkaryash/LMS
