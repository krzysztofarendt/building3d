.PHONY: format lint lint-full test coverage count count-tests example_1 example_2 example_3 example_4 example_5 examples test_publish publish

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
	pytest --cov=building3d --cov-report=xml --cov-report=term-missing tests/

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

example_4:
	python examples/example_4.py

example_5:
	python examples/example_5.py

examples:
	python examples/example_1.py
	python examples/example_2.py
	python examples/example_3.py
	python examples/example_4.py
	python examples/example_5.py
	python examples/read_teapot.py
	python examples/read_write_dotbim.py

test_publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository testpypi dist/*

publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository pypi dist/*
