ALL := template-etc-default-vpc.yml template-etc-custom-vpc.yml

.PHONY: src

all: ${ALL}

template-etc-default-vpc.yml: src
	ln -fv src/$@ $@

template-etc-custom-vpc.yml: src
	ln -fv src/$@ $@

src:
	$(MAKE) -C $@

clean:
	rm -f ${ALL}
	$(MAKE) -C src clean
