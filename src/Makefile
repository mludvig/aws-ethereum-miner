ALL := template-etc-default-vpc.yml template-etc-custom-vpc.yml

PYLINT := pylint --disable=invalid-name,line-too-long,missing-docstring,bad-whitespace

PY_ORIGS := lambdas/instance-filter.py lambdas/asg-updater.py
PY_MINIS := ${PY_ORIGS:py=min.py}

all: ${ALL}

clean:
	rm -f ${PY_MINIS} ${ALL}

template-etc-default-vpc.yml: template-etc-default-vpc.template.yml ${PY_MINIS} import-files.py ami-ids.yml user-data-runner.txt
	python3 import-files.py --yaml $< > $@

template-etc-custom-vpc.yml: template-etc-custom-vpc.template.yml ${PY_MINIS} import-files.py ami-ids.yml user-data-runner.txt
	python3 import-files.py --yaml $< > $@

%.min.py: %.py
	$(PYLINT) --exit-zero $<
	$(PYLINT) -E $<
	pyminifier $< > $@
