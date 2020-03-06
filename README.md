# Drive Publisher

This tool publishes to a Google Drive sheet whatever content tubed in stdin

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


