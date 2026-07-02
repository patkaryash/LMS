# PR Workflow Comment Task — Step-by-Step Runbook

This document decomposes the LMS PR workflow comment task into discrete, verifiable steps. Each step produces a concrete artifact or check, and steps can be skipped independently when they are already complete.

## Workflow Goal

When an issue instructs the agent to add a PR workflow comment to the LMS repository, the agent must:

1. Identify the source change (README, code file, etc.) requested by the issue.
2. Draft the comment text locally and verify it against the issue context.
3. Post the comment on the relevant pull request or commit.
4. Verify the comment appears correctly.
5. Update the issue status and record evidence.

## Discrete Steps

### Step 1 — Draft comment

**Action:** Produce a comment body that addresses the issue exactly.

- Read the issue description and acceptance criteria.
- Read the relevant file/PR context.
- Draft the comment in a temporary buffer or file (`/tmp/pr_comment.md` or `.paperclip/artifacts/pr_comment.md`).

**Artifact:**

- Local file containing the proposed comment text.
- Issue context summary (what change the comment refers to).

**Skip condition:**

- A comment draft file already exists and matches the issue context.

**Evidence format:**

```text
Draft: <path to draft file>
Issue: <issue identifier>
Context: <one-line summary>
```

---

### Step 2 — Validate against context

**Action:** Confirm the drafted comment is appropriate for the issue and target PR.

- Check that the comment references the correct issue identifier.
- Check that the comment tone matches project conventions (concise, technical, no AI-isms).
- Check that the comment does not contain secrets or unrelated content.

**Artifact:**

- Validation checklist (inline in the run log or as a small JSON file).

**Skip condition:**

- The same draft was validated in a previous run and the issue context has not changed.

**Evidence format:**

```text
Validation: passed
Checks:
  - Issue reference correct: yes
  - Tone appropriate: yes
  - No secrets: yes
  - Context unchanged: yes
```

---

### Step 3 — Post comment

**Action:** Submit the comment to the relevant GitHub PR or commit.

- Locate the target PR via the issue's linked work products or by searching open PRs.
- Post the comment using the GitHub REST API (`POST /repos/{owner}/{repo}/issues/{number}/comments`).

**Artifact:**

- GitHub comment URL returned by the API.

**Skip condition:**

- A comment URL already exists in the issue's work products or comments for this run.

**Evidence format:**

```text
Posted comment: https://github.com/patkaryash/LMS/pull/<pr>/issuecomment/<id>
Author: <agent>
Timestamp: <ISO8601>
```

---

### Step 4 — Verify posted comment

**Action:** Fetch the comment from GitHub and confirm it matches the draft.

- `GET /repos/{owner}/{repo}/issues/comments/{comment_id}`
- Compare the returned `body` with the draft.

**Artifact:**

- Fetched comment body (first 500 characters) or a diff showing it matches.

**Skip condition:**

- Verification was performed in a previous run and the comment has not been edited.

**Evidence format:**

```text
Verification: passed
Fetched comment excerpt: <first 500 chars>
Matches draft: yes
```

---

### Step 5 — Update issue status

**Action:** Mark the issue as done and add a completion comment with evidence.

- Set status to `done` via the Paperclip API.
- Post a concise comment summarizing Steps 1–4 and linking the PR comment.

**Artifact:**

- Issue status update response.
- Completion comment on the issue.

**Skip condition:**

- Issue status is already `done` and the completion comment is present.

**Evidence format:**

```text
Status: done
Completed at: <ISO8601>
Evidence:
  - Draft: <path>
  - Validation: passed
  - Comment URL: <url>
  - Verification: passed
```

## Idempotency and Churn Prevention

Each step stores its key artifact in the issue's work products or comments. Before executing a step, the agent must check whether the artifact already exists and is still valid. If all five artifacts are present and valid, the run should exit without re-posting or re-updating the issue.

## Evidence Template

When marking a PR comment workflow issue complete, use this exact template in the completion comment:

```markdown
Done. Issue: `<issue-identifier>`
- Draft: `<draft-path>`
- Validation: passed
- Posted comment: `<github-comment-url>`
- Verification: passed
- Status: `done`
```
