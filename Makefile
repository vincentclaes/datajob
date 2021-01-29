install:
	pip3 install poetry
	poetry config virtualenvs.create true
	poetry install


install-dev:
	make install
	# install pre commit hooks to check the code
	# before committing.
	poetry run pre-commit install

tests:
	poetry run pytest

run-examples:
	cd "${CURDIR}/examples/data_pipeline_simple" && poetry run datajob synthesize --config datajob_stack.py --stage dev
	cd "${CURDIR}/examples/data_pipeline_with_packaged_project" && poetry run datajob synthesize --config datajob_stack.py --stage dev --package poetry
	cd "${CURDIR}/examples/data_pipeline_with_packaged_project" && poetry run datajob synthesize --config datajob_stack.py --stage dev --package setuppy

gh-actions:
	make install
	make tests
	make run-examples
