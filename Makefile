ALL := template-eth-default-vpc.yml template-eth-custom-vpc.yml

.PHONY: src

all: ${ALL}

template-eth-default-vpc.yml: src
	ln -fv src/$@ $@

template-eth-custom-vpc.yml: src
	ln -fv src/$@ $@

src:
	$(MAKE) -C $@

clean:
	rm -f ${ALL}
	$(MAKE) -C src clean
