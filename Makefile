.PHONY: install
install:
	pip install -e .
	python .setup_git_hooks.py
