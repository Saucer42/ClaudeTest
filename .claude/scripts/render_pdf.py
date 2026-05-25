"""Render a Markdown source to PDF via Pandoc.

Deterministic, no LLM involvement. Wraps:

    pandoc <source.md> \
      --defaults templates/pandoc-defaults.yaml \
      --template templates/<template-name>.tex \
      -o <source>.pdf

Inputs
------
- source : Path  — path to a Markdown source file.
- template_name : str  — one of {'resume', 'cover-letter'} (resolved to
  templates/<template-name>.tex).

Outputs
-------
- A PDF written next to the source Markdown (same basename, .pdf suffix).
- Returns the path to the generated PDF.

Behaviour
---------
- Verifies the source file exists.
- Verifies the template file exists in templates/.
- Verifies `pandoc` and `xelatex` are on PATH; raises with a clear message
  if missing.
- Surfaces Pandoc stderr verbatim on failure.

TODO
----
- Implement the subprocess invocation, error surfacing, and path return.
- Decide whether to suppress Pandoc's stdout chatter on success.
"""

from __future__ import annotations


def main() -> None:
    """Entry point. TODO: implement."""
    raise NotImplementedError("render_pdf: see module docstring")


if __name__ == "__main__":
    main()
