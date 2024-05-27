.PHONY: format lint lint-full test coverage count count-tests example_1 example_2 example_3 test_publish publish

format:
	black $(shell ls **/*.py)
	isort --sl $(shell ls **/*.py)

lint:
	flake8 --select=E9,F63,F7,F82,E501 --max-complexity=10 --max-line-length=100 --show-source --statistics building3d/

lint-full:
	flake8 --max-complexity=10 --max-line-length=100 --show-source --statistics building3d/

test:
	pytest tests/

coverage:
	pytest --cov=building3d tests/

count:
	cloc --by-file building3d/

count-tests:
	cloc --by-file building3d/ tests/

example_1:
	python examples/example_1.py

example_2:
	python examples/example_2.py

example_3:
	python examples/example_3.py

test_publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository testpypi dist/*

publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository pypi dist/*
