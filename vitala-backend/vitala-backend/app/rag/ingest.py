"""Build or rebuild the knowledge index.

    python -m app.rag.ingest          # build if empty
    python -m app.rag.ingest --reset  # wipe and rebuild
"""
import sys

from .store import build_index, ensure_index


def main():
    reset = "--reset" in sys.argv
    if reset:
        n = build_index(reset=True)
        print(f"Rebuilt knowledge index: {n} chunks.")
    else:
        n = ensure_index()
        print(f"Knowledge index ready ({n} chunks added)." if n else "Knowledge index already built.")


if __name__ == "__main__":
    main()
