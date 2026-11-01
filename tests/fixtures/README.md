# Test fixtures

Fixtures will hold **synthetic, sanitized inputs** for the analysis engine — never
copies of real published packages or registry responses that carry someone else's
copyrighted code.

Planned contents, added when the module that needs them lands:

| File | Used by | Purpose |
|---|---|---|
| `npm_manifest_minimal.json` | `fetchers/` | A trimmed npm registry document with one version entry |
| `source_tree_minimal/` | `analyzer/` | A tiny hand-written "source" tree to hash and compare |
| `package_tree_minimal/` | `analyzer/` | The matching "published" tree, differing only by compiled output |
| `provenance_attestation.json` | `provenance/` | A crafted in-toto statement with a deliberately broken signature |

Rules for anything added here:

- Small and readable enough to review in a pull request.
- No credentials, tokens, real user data, or vendored third-party source.
- Malicious examples are fictional payloads, never a real-world supply-chain implant.
- Generated fixtures get a comment saying how to regenerate them, so they stay
  reproducible.

This directory is empty of code by design in Milestone 0.1: there is nothing yet that
consumes a fixture.
