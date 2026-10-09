.PHONY: train api ui clean

train:
	python scripts/train_models.py

api:
	cd predictive_maintenance_api && uvicorn main:app --reload --port 8000

ui:
	cd predictive-ui && npm install && npm start

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
