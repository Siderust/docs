SHELL := /bin/bash

IMAGE_NAME ?= siderust-manuscript-tex
TEXLIVE_IMAGE ?= texlive/texlive:TL2025-historic
PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)
DOCKER_RUN := docker run --rm --user "$(UID):$(GID)" -e HOME=/tmp -v "$(PWD):/workspace" -w /workspace/tex $(IMAGE_NAME)
CHKTEX_FLAGS := -q -n2 -n8 -n13 -n18 -n24

.DEFAULT_GOAL := pdf
.PHONY: pdf lint examples check clean docker-build

docker-build:
	docker build --build-arg TEXLIVE_IMAGE=$(TEXLIVE_IMAGE) -t $(IMAGE_NAME) docker

pdf: docker-build
	$(DOCKER_RUN) latexmk -pdf -interaction=nonstopmode -file-line-error main.tex
	@test -f tex/main.pdf

lint: docker-build
	$(DOCKER_RUN) chktex $(CHKTEX_FLAGS) main.tex

examples:
	cargo check --locked --manifest-path examples/Cargo.toml --bins

check: pdf lint examples

clean: docker-build
	$(DOCKER_RUN) latexmk -C main.tex
