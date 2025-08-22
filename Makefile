.PHONY: venv run add-cases-prod

venv:
	@echo "Setting up virtual environment..."
	@uv venv --clear
	@uv sync --dev

run:
	@echo "Running all cases..."
	@uv run -m lpo_measure run

add-cases-prod:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make add-cases-prod FILE=<path-to-instructions-file>"; \
		exit 1; \
	fi
	@echo "Adding cases from $(FILE) to production database..."
	@CI=true uv run -m lpo_measure add $(FILE)
