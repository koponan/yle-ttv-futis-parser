.PHONY: test profile

test:
	python3 -m unittest discover -s test -p "*test.py" -v

profile:
	python3 -m test.profile
