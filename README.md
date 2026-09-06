# Design Verification: From First Principles to Agentic AI

An open textbook for engineers who verify silicon. Written in public with
Quarto; every listing is a runnable file that CI compiles before a release.

- **Read online:** https://mayurkubavat.github.io/dv-handbook
- **PDF:** attached to each [release](https://github.com/mayurkubavat/dv-handbook/releases)
- **License:** CC BY-NC-SA 4.0 for the text, MIT for the code (see `LICENSE.md`)

## Build locally
```bash
brew install librsvg poppler verilator icarus-verilog systemc
brew install --cask font-source-sans-3 font-source-serif-4 font-jetbrains-mono
conda create -n dvbook python=3.12 && conda run -n dvbook pip install cocotb pyuvm
# Quarto: https://quarto.org/docs/get-started/  (any 1.6+)
scripts/check-examples.sh      # lint + run every example
scripts/build-book.sh          # _book/Design-Verification-draft.pdf
```

## Status
See `STATUS.md` for the current milestone and chapter states. Errata and
suggestions: open an issue and mention the chapter.
