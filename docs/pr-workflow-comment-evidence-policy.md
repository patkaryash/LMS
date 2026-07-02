# PR Workflow Comment Task — Evidence-Before-Done Policy

## Scope
This policy applies to every Paperclip agent run assigned to a PR workflow comment task (e.g., YAS-46 and its decomposed children). It prevents run churn by requiring a verifiable artifact before an issue can be marked `done`.

## Acceptance criteria
1. Before the issue transitions to `done`, the run must capture a verifiable artifact:
   - GitHub PR comment URL and comment ID, or
   - Commit SHA / diff link for a code change, or
   - Screenshot or exported log of the posted artifact.
2. `done` is rejected if no evidence is present.
3. The evidence is visible to the board in the issue comments or linked artifact.

## Evidence gate checklist
- [ ] The artifact exists in the remote repository / PR / issue.
- [ ] The artifact URL or ID is recorded in the work product comment on the issue.
- [ ] The artifact content matches the intended task outcome.
- [ ] The run reports the evidence before calling the issue `done`.

## Verification steps
1. Inspect the PR/issue comments for a link or reference.
2. Use `scripts/verify_pr_workflow_evidence.py` to confirm the artifact is reachable.
3. If the script returns `PASS`, the evidence gate is satisfied.

## Related issues
- YAS-151: Enforce evidence-before-done policy (this policy)
- YAS-166: Implement evidence-before-done gate for PR workflow comment task
- YAS-174: Implement idempotency check for PR workflow comment task
