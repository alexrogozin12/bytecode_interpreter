### Interpreter of Python bytecode.

#### Yandex School for Data Analysis Python course, Fall 2018.

Implements a virtual machine (```vm.py```) that runs Python bytecode (previously compiled from raw text). The virtual machine emulates a Python interpreter and supports the following structures.

1. Basic operations: arithmetics, braces, number and boolean types.
1. ```if```, ```for```, ```while``` statements.
1. Strings and formatting.
1. Lists, dicts, tuples, list generators, slices.
1. Functions.
1. Classes (simple cases)

To launch the VM on the test cases, run 
```
python3 vm.py
```