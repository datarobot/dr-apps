.PHONY: clean req-test test lint

clean:
	find . -path '*/__pycache__/*' -delete
	find . -type d -name __pycache__ -delete
	rm -rf .mypy_cache .pytest_cache dist build *.egg-info

req-test:
	pip install --upgrade pip==20.3.4
	pip install -e .[test]

test:
	echo "NO TESTS"
# 	py.test -sv tests/

black:
	black ./bin ./drapps ./tests -S -l 100

black-check:
	black ./bin ./drapps ./tests -S --check -l 100

isort:
	isort ./bin ./drapps ./tests

isort-check:
	isort -c ./bin ./drapps ./tests

mypy:
	mypy --config-file=mypy.ini ./drapps

flake:
	flake8 bin drapps tests

lint: isort-check black-check mypy flake
