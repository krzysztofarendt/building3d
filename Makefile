.PHONY: format lint lint-full test coverage count count-tests examples test_publish publish

format:
	black $(shell ls **/*.py)
	isort --sl $(shell ls **/*.py)

lint:
	flake8 --select=E9,F63,F7,F82,E501 --max-complexity=10 --max-line-length=100 --show-source --statistics building3d/

lint-full:
	flake8 --max-complexity=10 --max-line-length=100 --show-source --statistics building3d/

test:
	pytest tests/

test-numba:
	NUMBA_DISABLE_JIT=1 pytest tests/numba/
	NUMBA_DISABLE_JIT=0 pytest tests/numba/

coverage:
	pytest --cov=building3d --cov-report=xml --cov-report=term-missing tests/

count:
	cloc --by-file building3d/

count-tests:
	cloc --by-file building3d/ tests/

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
