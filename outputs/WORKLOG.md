# Ising Model Assignment Work Log

This log records the evidence workflow for the eight assignment sections. It is
updated after each section with sources, tasks, outputs, commands, numerical
results, validation, commit reference, and draft-writing notes.

## Section 1 - Introduction to the Ising Model

PDF name:
- `script/1_introduction.pdf`
- Background theory from `Introduction.pdf`

Task labels completed:
- Section 1 background theory preparation.

Code/data/figure files produced:
- `outputs/notes/section_1_background.md`
- Output scaffold:
  - `outputs/data/generated/`
  - `outputs/data/processed/`
  - `outputs/figures/`
  - `outputs/logs/`
  - `outputs/notes/`

Commands run:
- Extracted PDF text with bundled `pypdf` runtime into `/private/tmp/ising_pdf_text`.
- `mkdir -p outputs/data/generated outputs/data/processed outputs/figures outputs/logs outputs/notes`

Key numerical results:
- Exact infinite-size 2D square-lattice critical temperature noted for later
  comparison: `T_C = 2 / ln(1 + sqrt(2)) = 2.269185...`.

Validation outcome:
- PDF sources were readable with `pypdf`.
- Notes cover Hamiltonian, periodic boundaries, magnetisation, spontaneous
  magnetisation, reduced units, and critical-temperature context.

Commit reference:
- Section commit message: `Section 1: add Ising model background notes`
- Commit hash: assigned by Git when this section entry is committed.

Draft-writing notes:
- Use the background note as the report opening.
- Emphasise finite-size peak temperatures as estimates rather than true
  thermodynamic-limit transitions.
