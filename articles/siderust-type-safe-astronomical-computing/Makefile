SHELL := /bin/bash

IMAGE_NAME ?= siderust-manuscript-tex
TEXLIVE_IMAGE ?= texlive/texlive:TL2025-historic
REPO := $(abspath ../..)
ARTICLE_PATH := articles/$(notdir $(CURDIR))
UID := $(shell id -u)
GID := $(shell id -g)
DOCKER_RUN := docker run --rm --user "$(UID):$(GID)" -e HOME=/tmp -v "$(REPO):/workspace" -w /workspace/$(ARTICLE_PATH) $(IMAGE_NAME)
CHKTEX_FLAGS := -q -n2 -n8 -n13 -n18 -n24

.DEFAULT_GOAL := pdf
.PHONY: pdf lint fmt fmt-check integrity tables-check examples check clean docker-build

docker-build:
	docker build --build-arg TEXLIVE_IMAGE=$(TEXLIVE_IMAGE) -t $(IMAGE_NAME) docker

pdf: docker-build
	$(DOCKER_RUN) sh -c 'cd tex && latexmk -pdf -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build main.tex'
	@test -f tex/build/main.pdf

lint: docker-build
	$(DOCKER_RUN) sh -c 'cd tex && chktex $(CHKTEX_FLAGS) main.tex'

examples:
	cargo check --locked --manifest-path examples/Cargo.toml --bins

fmt fmt-check: docker-build
	$(DOCKER_RUN) python3 /workspace/scripts/tex-quality.py $@ .

integrity:
	python3 experiments/results/verify.py

tables-check:
	bash experiments/reproduce.sh --tables tables-$$(date -u +%Y%m%dT%H%M%S)-$$$$

check: fmt-check pdf lint examples integrity tables-check

clean: docker-build
	$(DOCKER_RUN) sh -c 'cd tex && latexmk -C -outdir=build main.tex'
