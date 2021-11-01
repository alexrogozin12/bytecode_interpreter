import filecmp
import sys
import os
from contextlib import redirect_stdout
from os.path import isfile, join

global_names = globals()
local_names = locals()


def run_vm(vm):
    run_tests_in_dir(vm, './Tests/')
    run_tests_in_dir(vm, './Tests/From_500lines/')


def run_tests_in_dir(vm, path='./Tests/'):
    tests = [file for file in os.listdir(path) if isfile(join(path, file))]
    correct_count = 0
    test_count = 0
    for test_name in tests:
        try:
            correct = run_test(vm, test_name, dir_name=path)
            correct_count += int(correct)
        except AttributeError:
            pass
        test_count += 1

    print('======================================\n{}: passed {}/{} tests\n'
          '======================================'
          .format(path, correct_count, test_count))


def run_test(vm, test_name, dir_name='./Tests/'):
    os.system('rm ./true_res.txt')

    with open('{}{}'.format(dir_name, test_name)) as source:
        code = source.read()

    true_res = open('true_res.txt', 'w')
    with redirect_stdout(true_res) as output:
        exec(code, global_names, local_names)
    true_res.close()

    vm_res = open('vm_res.txt', 'w')
    with redirect_stdout(vm_res) as output:
        vm.run_code(code)
    vm_res.close()

    if filecmp.cmp('vm_res.txt', 'true_res.txt'):
        print('{}: correct'.format(test_name))
        test_correct = True
    else:
        with open('vm_res.txt', 'r') as vm_res:
            with open('true_res.txt', 'r') as true_res:
                print('{} error:\nvm_res:\n{}\ntrue_res:\n{}'
                      .format(test_name, vm_res.read(), true_res.read()))
        test_correct = False
    return test_correct


def run_vm_on_file(vm, filename):
    with open(filename, 'r') as source:
        code = source.read()
    vm.run_code(code)


class TrueInterpreter(object):
    def __init__(self):
        pass

    def run_code(self, code):
        exec(code)
