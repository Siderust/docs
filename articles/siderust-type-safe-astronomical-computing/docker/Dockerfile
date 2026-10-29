# syntax=docker/dockerfile:1
# LaTeX manuscript build environment.
#
# The default image intentionally uses a year-pinned TeX Live snapshot instead of
# `latest`, so manuscript layout and package behavior do not drift implicitly.
# Override TEXLIVE_IMAGE only for deliberate compatibility testing.

ARG TEXLIVE_IMAGE=texlive/texlive:TL2025-historic
FROM ${TEXLIVE_IMAGE}

WORKDIR /workspace

# Fail the image build immediately if required tooling is absent from the TeX
# Live image. Do not mask missing tools with informational echo commands.
RUN command -v latexmk >/dev/null \
    && command -v biber >/dev/null \
    && command -v chktex >/dev/null

CMD ["/bin/bash"]
