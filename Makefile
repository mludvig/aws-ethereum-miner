ALL := template-default-vpc.yml template-custom-vpc.yml

.PHONY: src

all: ${ALL}

template-default-vpc.yml: src
	ln -fv src/$@ $@

template-custom-vpc.yml: src
	ln -fv src/$@ $@

src:
	$(MAKE) -C $@

clean:
	rm -f ${ALL}
	$(MAKE) -C src clean
