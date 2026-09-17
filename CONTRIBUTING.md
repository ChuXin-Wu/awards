# Contributing

Contributions maintain the public problem bank, evidence, candidate records, and announced awards. Submitting an issue or passing repository checks does not announce an award.

## Four ways to participate

| Type | Include | Handling |
| --- | --- | --- |
| Recommend a problem | Precise statement, significance, original references, known results, formalization links | Maintainers check scope, sources and duplicates. |
| Recommend a recipient | Placeholder or confirmed public ID, contribution description, evidence, related entry | Maintainers review attribution evidence. |
| Correction | Exact record, current text, proposed correction and supporting sources | Maintainers review the evidence and record the outcome. |
| Dispute | Announced award, disputed claim, evidence, requested resolution and conflicts | Maintainers record the concern and arrange review. |

Use the corresponding [issue form](.github/ISSUE_TEMPLATE/). Link existing issues instead of duplicating them. Disclose relevant conflicts using public professional information only. Use RECIPIENT-<ENTRY>-A placeholders until recipient identities are confirmed. Never publish unconfirmed identities, private contacts, identity documents, payment details, internal assessment criteria or deliberations, including in commit messages.

## Public records

Candidates and announced awards remain separate. Candidate records contain public facts and review evidence; an announced decision belongs only in an award record linked to its public announcement. Do not import internal assessment worksheets or calculation rules.

Formal evidence references identify a pinned proof source, a statement tied to the original problem, and supporting verification records. Only authorized public evidence belongs here. Successful repository checks do not certify the mathematical content.

Keep recipient identities as placeholders until confirmation. Announced awards require completed verification evidence, confirmed public profiles and explicit batch membership. A revocation retains the original decision, recipients and evidence alongside the published reason.

Recommendations, corrections and disputes should receive a public response in their issue thread. [Discussions](docs/discussions-notice.md) is for general conversation. Refer to published announcements for any applicable submission requirements; these forms do not establish an assessment or appeals procedure.

## Pull requests

- Write repository documents and records in English. Keep documentation, templates and schemas consistent.
- Use the [record guide and templates](docs/records.md); keep synthetic examples outside live record directories.
- Include public evidence and a clear reason for status changes.
- Run validation, tests and data generation, then include generated JSON changes.
- Review the complete diff and commit history for private material before submitting.

Licensing is governed by [LICENSE](LICENSE) and [LICENSE-CONTENT](LICENSE-CONTENT). Only submit material you are entitled to contribute; retain third-party attribution and licenses.

## External solver and Lean submissions

**Only complete solutions to the original problem are accepted. Partial progress
is not eligible for submission, whether mathematical or in Lean.**

Mathematical submissions must resolve the full original statement, including all
required cases. Special cases, intermediate lemmas, weaker results and conditional
arguments that depend on additional unproved assumptions are not accepted.

Lean submissions must provide a complete formal proof of the original problem at
the specified commit. A statement alone, a partial formalization, or a proof that
depends on `sorry`, `admit` or unproved assumptions added to stand in for missing
proof steps is not accepted. A complete mathematical solution does not make an
incomplete Lean formalization eligible for submission. Reviewers must verify
completeness before approving a PR.

Use the default PR template and edit the relevant existing
`problems/catalog-XXXX-XXXX.md` file. External PRs may update **Current status**
(including mathematical solver credits), **Lean proof**, **Attribution basis**, and
**Publication details**. Use only **Open** or **Solved** as the status; record
complete-solution credits in the same **Current status** field after
**Proof contributors:**. Do not add intermediate results or incomplete
formalizations. Explain proposed status changes for maintainer review;
maintainers reconcile index/status/eligibility fields after review. Use issues for
other corrections or requests rather than changing unrelated repository files.

Provide evidence according to the contribution:

- **Solver information:** link the public proof or publication and sources supporting
  the named solver's contribution, such as the paper's author list or an author
  announcement. Identify the relevant theorem, version or pages.
- **Lean information:** link the public source repository and supply its branch and
  a full 40-character commit SHA. Identify the theorem/file, formalization authors,
  build instructions and attribution evidence in that repository.
- **Both:** provide both sets of evidence. Solver-only corrections do not require
  a Lean repository.

Submit references and catalog text only. Do not commit Lean source, project/build
files, dependencies, archives or binaries to this repository. Do not paste proof
source into catalog rows. Update an existing PR for the same contribution instead
of opening duplicates. Existing PRs containing source should be revised to remove
those files and use this format; they are not automatically closed.

Maintainer review and approval are required before merging. Reviewers check
source accessibility, the pinned version, attribution and the full theorem scope,
including whether the named branch contains the selected commit.
