.PHONY: release test


artifacts: test
	python setup.py sdist


release: test
	python setup.py sdist upload


test:
	pytest