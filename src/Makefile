ALL := template-eth-default-vpc.yml template-eth-custom-vpc.yml

PYLINT := pylint --disable=invalid-name,line-too-long,missing-docstring,bad-whitespace

PY_ORIGS := lambdas/instance-filter.py lambdas/asg-updater.py
PY_MINIS := ${PY_ORIGS:py=min.py}

all: ${ALL}

clean:
	rm -f ${PY_MINIS} ${ALL}

%.yml: %.template.yml ${PY_MINIS} import-files.py
	python3 import-files.py --yaml $< > $@

%.min.py: %.py
	$(PYLINT) --exit-zero $<
	$(PYLINT) -E $<
	pyminifier $< > $@
