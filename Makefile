install:
	@poetry install
	@poetry run pre-commit install -f

update:
	@poetry update
	@poetry run pre-commit autoupdate

test:
	@poetry run pytest -v -x -p no:warnings --cov-report term-missing --cov=./marshmallow_pynamodb

ci:
	@poetry run pytest --cov=./marshmallow_pynamodb --black --flake8

format:
	@poetry run black .

dynamodb:
	docker run -p 8000:8000 amazon/dynamodb-local
changelog:
	echo "TODO"
release:
	echo "TODO"
deploy:
	python setup.py sdist bdist_wheel
	twine upload dist/*
