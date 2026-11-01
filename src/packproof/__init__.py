"""PackProof — prove what's inside your packages.

Supply-chain integrity analyzer that compares a published npm package against the
source repository revision it claims to have been built from.

`__version__` is the authoritative version for the whole project. `pyproject.toml`
declares `dynamic = ["version"]` and reads this literal at build time through
`[tool.hatch.version]`, so a release changes exactly one line and runtime code never
has to look the version up in installed package metadata.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
