.PHONY: clean req-test test lint cli-plugin package-cli-plugin publish-cli-plugin

clean:
	find . -path '*/__pycache__/*' -delete
	find . -type d -name __pycache__ -delete
	rm -rf .mypy_cache .pytest_cache dist build *.egg-info

req-test:
	pip install --upgrade pip==20.3.4
	pip install --no-use-pep517 -e .[test]

req:
	pip install --upgrade pip==20.3.4
	pip install --no-use-pep517 .

test:
	py.test -sv tests/ --log-cli-level=DEBUG
	py.test -sv examples/prediction-demo/tests/ --log-cli-level=DEBUG

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

# CLI Plugin packaging targets
cli-plugin:
	@echo "Building wheel..."
	@python setup.py bdist_wheel
	@./bin/build-cli-plugin

package-cli-plugin: cli-plugin
	@echo "Packaging CLI plugin..."
	@if ! command -v dr &> /dev/null; then \
		echo "Error: 'dr' CLI not found. Please install DataRobot CLI first."; \
		exit 1; \
	fi
	@dr self plugin package dist/plugin-staging $(PLUGIN_PACKAGE_FLAGS)
	@echo "✅ Plugin packaged successfully"

publish-cli-plugin: cli-plugin
	@echo "Publishing CLI plugin..."
	@if ! command -v dr &> /dev/null; then \
		echo "Error: 'dr' CLI not found. Please install DataRobot CLI first."; \
		exit 1; \
	fi
	@dr self plugin publish dist/plugin-staging $(PLUGIN_PUBLISH_FLAGS)
	@echo "✅ Plugin published successfully"
