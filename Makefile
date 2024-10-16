.PHONY: format lint lint-full test coverage count count-tests examples test_publish publish

format:
	black --line-length=100 $(shell ls **/*.py)
	isort --sl $(shell ls **/*.py)

lint:
	flake8 --select=E9,F63,F7,F82,E501 --max-complexity=10 --max-line-length=100 --show-source --statistics building3d/

lint-full:
	flake8 --max-complexity=10 --max-line-length=100 --show-source --statistics building3d/

test:
	NUMBA_DISABLE_JIT=1 pytest tests/
	NUMBA_DISABLE_JIT=0 pytest tests/

coverage:
	NUMBA_DISABLE_JIT=1 pytest --cov=building3d --cov-report=xml --cov-report=term-missing tests/

count:
	cloc --by-file building3d/

count-tests:
	cloc --by-file building3d/ tests/

examples:
	python examples/array_format_example.py
	python examples/building_example.py
	python examples/floor_plan_example.py
	python examples/polygon_example.py
	python examples/ray_2_boxes_example.py
	python examples/ray_cylinder_example.py
	python examples/ray_sphere_example.py
	python examples/ray_teapot_example.py
	python examples/read_teapot.py
	python examples/solid_example.py
	python examples/wall_example.py
	python examples/zone_example.py

test_publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository testpypi dist/*

publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository pypi dist/*
