## Submission type

- [ ] Mathematical solver information
- [ ] Lean proof or formalization author information

Select both when applicable. Remove sections that do not apply.

**Only complete solutions to the original problem are accepted. Do not submit
partial mathematical results or incomplete Lean formalizations.**

## Problem and proposed change

Problem ID(s): JSP-______

State the current entry and proposed correction. Distinguish the mathematical
solver, Lean formalization author and independent verifier. Explain each person's
contribution; a repository owner or PR submitter is not automatically the solver.

## Solver evidence

Required for solver attribution or publication updates; otherwise remove this section.

- Solver(s) and contribution: REPLACE_WITH_NAMES_AND_CONTRIBUTIONS
- Public proof or publication: REPLACE_WITH_HTTPS_LINK
- Authorship evidence (paper author list, author/project announcement, or another public attribution source): REPLACE_WITH_HTTPS_LINK_AND_EXPLANATION
- Relevant pages, theorem, version or date: REPLACE_WITH_DETAILS

Link publicly accessible evidence supporting the claimed result and attribution.
Explain any mismatch between paper authors, repository accounts and proposed
credits. Do not include private identity documents or contact/payment information.

## Proof source

**Do not submit Lean source code here; provide the public repository URL, branch and full commit SHA instead.**

Required for Lean proof or formalization attribution updates; otherwise remove this
section. Use the full 40-character commit SHA of the proof version selected for
review. Add an object for each additional proof repository.

```json
[
  {
    "repository": "https://github.com/OWNER/REPOSITORY",
    "branch": "REPLACE_WITH_BRANCH",
    "commit": "REPLACE_WITH_FULL_COMMIT_SHA"
  }
]
```

Identify the theorem/file proving the original problem and the formalization
authors. Link to build instructions and attribution evidence in that repository.
Explain how the pinned proof covers the full original statement and all required
cases, without missing proof steps or additional unproved assumptions.

## Submission checklist

- [ ] I changed only solver attribution, Lean proof information or supporting sources in the relevant catalog.
- [ ] I supplied the evidence required for the type of change above.
- [ ] The mathematical result fully solves the original problem. Any submitted Lean proof is complete at the specified commit, with no `sorry`, `admit` or added unproved assumptions in the proof of that result.
- [ ] This PR contains no proof source files, archives, binaries or vendored dependencies.
- [ ] Any Lean reference identifies a commit contained in the named branch and the exact version for review.

For unrelated corrections, use an issue.
