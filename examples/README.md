# Examples

Nothing here runs yet except the two foundation commands. Examples are added as the
features they demonstrate ship, so this directory never advertises capability the
release does not have.

## What works in 0.1.0

```bash
packproof --help
packproof --version
python -m packproof --help
```

## Planned examples

| File | Shows | Milestone |
|---|---|---|
| `scan-npm-package.md` | `packproof scan express@4.21.2` end to end | when `fetchers/` + `analyzer/` exist |
| `legitimate-build-output.md` | a TypeScript package whose compiled output is correctly classified as expected | when `detectors/` exists |
| `tampered-tarball.md` | a synthetic injected payload in an otherwise clean artifact | when `detectors/` exists |
| `provenance-verified.md` | a release with a valid npm provenance attestation | when `provenance/` exists |
| `report-outputs/` | one scan rendered as JSON, HTML, and PDF | when `reporting/` exists |

Synthetic fixtures live in `tests/fixtures/`, not here; this directory is for
human-readable walkthroughs of real scans.
