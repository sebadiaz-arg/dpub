# Drive Publisher

This tool publishes to a Google Drive sheet whatever content tubed in stdin

## Installation

It is recommended to install the dependencies in a virtual environment for not mangling
the host ones. You need to have *python3* installed on your system first

```sh
sudo apt install -y python3 python3-pip
```

then, you can create and activate your virtual env
```sh
sudo apt install -y virtualenv
python3 -m virtualenv -p python3 venv
source venv/bin/activate
```

and finally, install dependencies
```sh
pip install -r requirements.txt
```

You are now good to go

## Execution example

Provide any content and tube it to the script:
```sh
echo "LEÑE" | ./dpub.py 1o8wahJ8qTIlHgAMQIMhxFq9bBmfIrlFvoEhkAJ3APFg 'TEST!A1'
```

### Execution along with newman-reporter-msgs

This tools is thought to work along with [newman-reporter-msgs](https://github.com/robertomier/newman-reporter-msgs)

You have to launch newman with the collection, environment and any other stuff that
you wish to test. Then you can tube the std out to this script and provide
a *Drive Sheet ID* and a *Cell* within certain spreadsheet

here's an example:
```sh
newman run -e environment.json collection.json -r msgs | ./dpub.py 1o8wahJ8qTIlHgAMQIMhxFq9bBmfIrlFvoEhkAJ3APFg 'TEST!A1'
```

> NOTE: You have to provide the cells range between single quotes for command not to fail.
> Otherwise the character ! will take some meaning out of the literal one.


## Hack
It is recommended