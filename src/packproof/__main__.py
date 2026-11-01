"""Support for `python -m packproof`.

Delegates to the same entry point as the installed `packproof` console script, so
module execution and script execution cannot drift apart.
"""

from packproof.cli.main import main

if __name__ == "__main__":
    main()
