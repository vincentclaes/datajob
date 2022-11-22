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
	poetry run pytest --disable-warnings

run-examples:
	cd "${CURDIR}/examples/data_pipeline_simple" && poetry run cdk synth --app "python datajob_stack.py"
	cd "${CURDIR}/examples/data_pipeline_parallel" && poetry run cdk synth --app "python datajob_stack.py"
	cd "${CURDIR}/examples/data_pipeline_with_packaged_project" && poetry run python setup.py bdist_wheel && poetry run cdk synth --app "python datajob_stack.py"
# 	cd "${CURDIR}/examples/ml_pipeline_sagemaker_scikitlearn" && poetry run cdk synth --app "python datajob_stack.py"
#   cd "${CURDIR}/examples/data_pipeline_pyspark" && poetry run python setup.py bdist_wheel && poetry run cdk synth --app "python datajob_stack.py"

gh-actions:
	make install
	make tests
	make run-examples
