# PR Workflow Comment Runbook

> Issue: YAS-65 — Decompose PR workflow comment task into verifiable steps.  
> Source: YAS-46 (LMS)  
> Trigger: high churn from repeated no-op completions.

## Goal

Break the LMS PR workflow comment task into a small set of discrete, verifiable steps so that every agent run produces observable evidence and cannot silently re-mark the issue `done`.

## Verifiable steps

### 1. Locate the emission point

Before any comment is posted, identify the exact code path, workflow step, or API call that emits the assignee-run comment.

**Evidence required:**
- File path and line range of the emission point, or
- Workflow step name and URL, or
- API endpoint and request/response log excerpt.

**Exit gate:** If the emission point cannot be located, record the search artifacts and stop the run with status `blocked`.

### 2. Define one observable deliverable per run

Each run must produce exactly one concrete artifact from this set:
- A code change (commit + branch + push), or
- A posted GitHub issue/PR comment (with a URL), or
- A status update on an issue (with a timestamp), or
- A documented decision / runbook update.

**Evidence required:**
- The artifact URL or commit SHA, and
- A one-line description of what the run changed.

**Exit gate:** If a run would produce only a no-op comment, exit immediately without mutating issue state.

### 3. Split the comment task into discrete steps

A PR workflow comment run must follow this sequence:

1. **Draft** — Compose the comment body from the current context (issue, PR, repo state).
2. **Validate** — Confirm the comment references the correct PR/issue and contains no stale data.
3. **Post** — Publish the comment via the authenticated GitHub API.
4. **Verify** — Retrieve the comment and assert it is visible and contains the expected text.
5. **Update status** — Only after verification, mark the issue done and post the closing comment.

**Evidence required:**
- Draft: quoted text or a link to the draft file.
- Validate: list of assertions checked (e.g., PR number, branch name, issue title).
- Post: GitHub API response including the comment `id` and `html_url`.
- Verify: GET request to the comment URL and a text snippet.
- Update status: issue PATCH response showing the new status and a closing comment URL.

### 4. Add per-step evidence to the issue body / comments

Every step must leave a trace that can be audited without reading the agent transcript.

**Evidence format:**
- URL: `https://github.com/<owner>/<repo>/pull/<n>#issuecomment-<id>`
- Commit/PR: `https://github.com/<owner>/<repo>/pull/<n>` or `commit/<sha>`
- Quoted output: at least 2 lines of raw API or CLI output.
- Timestamp in UTC.

### 5. Instrument the workflow to skip completed steps

Before starting work, read the issue history and existing comments. If a matching artifact already exists, skip the corresponding step.

**Idempotency checks:**
- If the issue is already `done` and the closing comment is present, exit with no mutation.
- If a child issue for the same sub-task already exists, do not create a duplicate.
- If the PR comment from step 3 already exists, do not re-post it.

### 6. Review churn metrics after 3 runs

After the runbook is adopted, observe the next 3 runs linked to the issue.

**Metrics:**
- Number of runs per hour.
- Number of assignee-run comments per hour.
- Number of no-op completions.
- Number of duplicate child issues or comments.

**Target:** Runs per hour <= 1 and no duplicate artifacts for the same sub-task.

## Run checklist for YAS-65

- [ ] Locate emission point: identify the exact PR workflow step or API call.
- [ ] Define one observable deliverable per run.
- [ ] Document the discrete steps (draft / validate / post / verify / update status).
- [ ] Add per-step evidence requirements and example formats.
- [ ] Add idempotency checks to skip completed steps.
- [ ] Schedule churn review after 3 runs.

## Evidence for this run

- Branch: `test/yas-65-verifiable-steps-runbook`
- File added: `PR_WORKFLOW_COMMENT_RUNBOOK.md`
- Issue: YAS-65
- Source issue: YAS-46
- Repository: https://github.com/patkaryash/LMS
