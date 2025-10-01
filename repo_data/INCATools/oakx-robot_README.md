# oakx-robot: A robot plugin for OAK

This is a plugin for [OAK](https://incatools.github.io/ontology-access-kit/) that wraps [ROBOT](robot.obolibrary.org)

It provides a RobotImplementation (see [implementations](https://incatools.github.io/ontology-access-kit/implementations/index.html) of an OntologyInterface, so far this only implements
a portion of the [ValidatorInterface](https://incatools.github.io/ontology-access-kit/interfaces/validator.html)

Currently this is more of a demonstrator/proof of concept than a useful tool. For most purposes you will likely want to simply
use robot on the command line tool

## Selector

This plugin registers the `robot` scheme

Use `robot:path/to/ontology.owl` as the [selector](https://incatools.github.io/ontology-access-kit/selectors.html)

## Initial Setup

1. Install robot
2. Start robot python

run:

```
robot python &
```

## Command Line

The test folder contains an ontology with a deliberate error:

```bash
runoak -i robot:tests/input/go-nucleus-unsat.owl validate
```

yields:

|type|severity|subject|instantiates|predicate|object|object_str|source|info
|---|---|---|---|---|---|---|---|---|
|owl:Nothing|ERROR|GO:0031965|None|None|None|None|None|None


## Programmatic

See [tests](tests/)

```python
from oaklib.selector import get_resource_from_shorthand, discovered_plugins, get_implementation_from_shorthand
from oakx_robot.robot_implementation import RobotImplementation, OWL_NOTHING

path = 'tests/input/go-nucleus-unsat.owl'
oi = get_implementation_from_shorthand(f'robot:{path}')
if oi.is_coherent():
    print('Congratulations! The ontology is coherent')
else:
    print('Reasoner detected usatisfiable classes')
    for c in oi.unsatisfiable_classes():
        print(f'Unsatisfiable: {c}')
```

## How it works

See [robot/python](https://robot.obolibrary.org/python)

## TODO

- Implement OwlInterface
- Implement more reasoning operations
- Allow selection of different reasoners
