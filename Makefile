setup:
	python -m pip install -r requirements.txt
load:
	python -m src.etl.pipeline
test:
	pytest -q
all:
	python -m src.etl.pipeline
	pytest -q

ratio-engine:
	python -m src.analytics.ratios
sprint2-test:
	pytest -q tests/kpi

sprint3-screener:
	python -m src.screener.run_all
sprint3-test:
	pytest -q
