# Makefile for Pitch Perfect Gradio
PYTHON_VERSION := 3.12.9
VENV_NAME := pp-gradio-env
PYTHON := python
PIP := pip
PROJECT_NAME := pitch-perfect-gradio

.PHONY: help
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

.PHONY: clean
clean: ## Clean up all generated files and caches
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	rm -rf build dist
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf flagged
	rm -rf gradio_cached_examples
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete

.PHONY: pyenv-install
pyenv-install: ## Install Python 3.12.9 via pyenv
	pyenv install -s $(PYTHON_VERSION)

.PHONY: venv
venv: pyenv-install ## Create virtual environment with pyenv
	pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME)
	@echo "Virtual environment created. Activate with: pyenv activate $(VENV_NAME)"

.PHONY: venv-activate
venv-activate: ## Show how to activate the virtual environment
	@echo "Run: pyenv activate $(VENV_NAME)"

.PHONY: venv-delete
venv-delete: ## Delete the virtual environment
	pyenv virtualenv-delete -f $(VENV_NAME)

.PHONY: install
install: ## Install dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

.PHONY: freeze
freeze: ## Update requirements.txt with current packages
	$(PIP) freeze > requirements.txt

.PHONY: analyze-deps
analyze-deps: ## Analyze and update dependencies
	$(PYTHON) scripts/analyze_requirements.py
	$(PYTHON) scripts/check_packages.py

.PHONY: format
format: ## Format code with black
	$(PIP) install black
	black *.py components/ utils/

.PHONY: lint
lint: ## Run linting
	$(PIP) install flake8
	flake8 *.py components/ utils/ --max-line-length=100 --ignore=E203,W503

.PHONY: run
run: check-env ## Run the application
	$(PYTHON) app.py

.PHONY: run-minimal
run-minimal: ## Run minimal UI version (no backend needed)
	$(PYTHON) app_minimal.py

.PHONY: docker-build
docker-build: ## Build Docker image
	docker build -t pitch-perfect-gradio:latest .

.PHONY: docker-run
docker-run: ## Run with Docker locally
	./deploy.sh local

.PHONY: docker-compose
docker-compose: ## Run with docker-compose
	docker-compose up

.PHONY: docker-clean
docker-clean: ## Clean up Docker containers
	./deploy.sh clean

.PHONY: deploy-gcp
deploy-gcp: ## Deploy to Google Cloud Platform
	./deploy.sh gcp


.PHONY: setup
setup: clean pyenv-install venv ## Complete setup from scratch
	@echo "✅ Setup complete!"
	@echo "1. Activate virtualenv: pyenv activate $(VENV_NAME)"
	@echo "2. Run: make install"
	@echo "3. Run: make check-env"
	@echo "4. Run: make run"

.PHONY: check-env
check-env: ## Check if .env file exists
	@if [ ! -f .env ]; then \
		echo "⚠️  .env file not found! Creating from .env.example..."; \
		cp .env.example .env; \
		echo "✅ Created .env file. Please update it with your configuration."; \
	else \
		echo "✅ .env file exists"; \
	fi

.PHONY: reset
reset: clean venv-delete ## Reset everything (delete venv and clean)
	@echo "✅ Reset complete. Run 'make setup' to start fresh."