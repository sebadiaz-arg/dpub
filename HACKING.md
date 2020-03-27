# Hacking

## Unitary tests

Unitary tests are implemented using pytest.

### install tox
You first must install tox:
```sh
python3 install tox
```

### Launch tox
If you want to launch tests in an isolated environment
```sh
tox
```

### Launch without tox
For development purposes, you can simplify the test execution
by launching with
```sh
python3 -m pytest test/
```

> NOTE: Don't use this shortcut in productive environments but tox one