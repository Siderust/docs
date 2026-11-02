# syntax=docker/dockerfile:1

ARG TEXLIVE_IMAGE=texlive/texlive:TL2025-historic
FROM ${TEXLIVE_IMAGE}

ARG RUST_VERSION=1.93.1
ARG USERNAME=texlive

ENV RUSTUP_HOME=/usr/local/rustup
ENV CARGO_HOME=/usr/local/cargo
ENV PATH="/usr/local/texlive/2025/bin/x86_64-linux:/usr/local/cargo/bin:${PATH}"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        ca-certificates \
        curl \
        git \
        pkg-config \
        python3 \
        python3-pip \
        python3-venv \
        make \
        sudo \
    && printf '%s ALL=(root) NOPASSWD:ALL\n' "${USERNAME}" > "/etc/sudoers.d/${USERNAME}" \
    && chmod 0440 "/etc/sudoers.d/${USERNAME}" \
    && rm -rf /var/lib/apt/lists/* \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --profile minimal --default-toolchain "${RUST_VERSION}" \
    && rustup component add rust-src \
    && command -v latexmk >/dev/null \
    && command -v latexindent >/dev/null \
    && command -v chktex >/dev/null \
    && command -v biber >/dev/null \
    && printf '%s\n' \
        'export PATH="/usr/local/texlive/2025/bin/x86_64-linux:/usr/local/cargo/bin:$PATH"' \
        > /etc/profile.d/siderust-toolchain.sh \
    && chown -R "${USERNAME}:${USERNAME}" "${CARGO_HOME}" \
    && chmod -R a+rX "${RUSTUP_HOME}" "${CARGO_HOME}"

WORKDIR /workspace

USER ${USERNAME}

CMD ["/bin/bash"]
