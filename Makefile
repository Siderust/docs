SHELL := /bin/bash
ARTICLE ?= siderust-type-safe-astronomical-computing
ARTICLE_DIR := articles/$(ARTICLE)
ARTICLES := $(sort $(patsubst articles/%/Makefile,%,$(wildcard articles/*/Makefile)))
.DEFAULT_GOAL := help

.PHONY: help pdf lint examples check pdf-all check-all

help:
	@echo "Articles: $(ARTICLES)"
	@echo "  make ARTICLE=siderust-type-safe-astronomical-computing pdf       Compile one manuscript"
	@echo "  make ARTICLE=siderust-type-safe-astronomical-computing lint      Run LaTeX language/style checks"
	@echo "  make ARTICLE=siderust-type-safe-astronomical-computing examples  Compile accompanying Rust examples"
	@echo "  make ARTICLE=siderust-type-safe-astronomical-computing check     Run all checks"
	@echo "  make pdf-all                   Build all articles"
	@echo "  make check-all                 Check all articles"

pdf lint examples check:
	@test -f "$(ARTICLE_DIR)/Makefile" || { echo "Unknown article: $(ARTICLE)"; exit 1; }
	+$(MAKE) -C "$(ARTICLE_DIR)" $@

pdf-all:
	@set -e; for article in $(ARTICLES); do $(MAKE) ARTICLE="$$article" pdf; done

check-all:
	@set -e; for article in $(ARTICLES); do $(MAKE) ARTICLE="$$article" check; done
