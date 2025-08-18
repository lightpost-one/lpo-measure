.PHONY: venv run

venv:
	@echo "Setting up virtual environment..."
	@uv venv --clear
	@uv sync --dev

run:
	@echo "Running LPO Measure..."
	@uv run -m lpo_measure
