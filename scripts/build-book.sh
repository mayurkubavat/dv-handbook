#!/usr/bin/env bash
# Render the book PDF with Quarto and bind the cover pages around it.
#   scripts/build-book.sh            -> _book/Design-Verification-draft.pdf
set -euo pipefail

# A citation that resolves is not a citation that prints; see the script.
"$(dirname "$0")/check-citations.sh" || exit 1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
export PATH="$HOME/.local/bin:$PATH"
./theme/cover/build_cover.sh >/dev/null
quarto render --to pdf
pdfseparate theme/cover/cover.pdf "$ROOT/_book/cover-%d.pdf"
pdfunite _book/cover-1.pdf _book/Design-Verification.pdf _book/cover-2.pdf _book/Design-Verification-draft.pdf
rm -f _book/cover-1.pdf _book/cover-2.pdf
pdfinfo _book/Design-Verification-draft.pdf | grep -E '^(Pages|Page size)'
