# Drive Publisher

This tool publishes to a Google Drive sheet whatever content tubed in stdin

## Installation

It is recommended to install the dependencies in a virtual environment for not mangling
the host ones. You need to have _python3_ installed on your system first

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

## Run the tool

There is a _run.sh_ launcher to execute the tool. It takes these parameters:

| parameter       | description                                                                                                                                                       | mandatory | example                                      |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | -------------------------------------------- |
| doc             | identifier of the spreadsheet where publishing                                                                                                                    | yes       | 1o8wahJ8qTIlHgAMQIMhxFq9bBmfIrlFvoEhkAJ3APFg |
| first test cell | cell where first test identifier is located                                                                                                                       | yes       | TEST!A2                                      |
| first msg cell  | cell where writing the results of the first test                                                                                                                  | yes       | TEST!C2                                      |
| -m --mode       | how to write into the spreadsheet. 'message' writes a message per cell; 'profile' writes every profile trace in a cell; 'test' writes every test in a single cell | no        | -m all                                       |

## Execution example

Provide any content and tube it to the script:

```sh
echo "whatever trace" | ./dpub.sh 1o8wahJ8qTIlHgAMQIMhxFq9bBmfIrlFvoEhkAJ3APFg 'TEST!A2' 'TEST!C2'
```

### Execution along with newman-reporter-msgs

This tools is thought to work along with [newman-reporter-msgs](https://github.com/robertomier/newman-reporter-msgs)

You have to launch newman with the collection, environment and any other stuff that
you wish to test. Then you can tube the std out to this script and provide
a _Drive Sheet ID_, a _Cell_ in certain spreadsheet where valid test identifiers are
and another _Cell_ in that same spreadsheet (could be even in another sheet) to write
the traces starting at that position

here's an example:

```sh
newman run -e environment.json collection.json -r msgs | ./dpub.sh 1o8wahJ8qTIlHgAMQIMhxFq9bBmfIrlFvoEhkAJ3APFg 'TEST!A2' 'TEST!C2'
```

This example reads in _TEST_ sheet, starting in _A2_ cell and moving in rows, all the test identifiers.
Traces will be printed starting in _C2_ cell. All traces belonging to the same test but different
profiles will be written in the next columns, in the same row. Different tests traces will be
written by moving vertically to the next tests.

> NOTE: You have to provide the cells range between single quotes for command not to fail.
> Otherwise the character ! will take some meaning out of the literal one.
