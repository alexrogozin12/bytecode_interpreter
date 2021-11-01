import dis
import builtins
import inspect
import operator
import types
from contextlib import redirect_stdout
import utils
from utils import run_vm


class Frame(object):
    def __init__(self, code, locals, globals, prev_frame):
        self.code = code
        self.ip = 0
        self.stack = []
        self.block_stack = []
        self.locals = locals
        self.globals = globals
        self.prev_frame = prev_frame
        if prev_frame:
            self.builtins = prev_frame.builtins
        else:
            self.builtins = builtins.__dict__

        self.cells = {}
        if self.code.co_cellvars:
            for var_name in self.code.co_cellvars:
                if var_name in self.locals:
                    cell = Cell(self.locals[var_name])
                else:
                    cell = Cell(None)
                self.cells[var_name] = cell
                if self.prev_frame:
                    self.prev_frame.cells[var_name] = cell

        if self.code.co_freevars and self.prev_frame:
            for var_name in self.code.co_freevars:
                self.cells[var_name] = self.prev_frame.cells[var_name]

        self.operators = {
            '==': operator.eq,
            '>=': operator.ge,
            '>': operator.gt,
            'is': operator.is_,
            'is not': operator.is_not,
            '<=': operator.le,
            '<': operator.lt,
            '!=': operator.ne,
            'not': operator.not_,
            'in': lambda a, b: operator.contains(b, a)
        }

    def init_instruction_set(self, instructions):
        self.instruction_set = []
        for instr in instructions:
            self.instruction_set += \
                [None] * (instr.offset - len(self.instruction_set)) + [instr]

    def dump(self, assignment='Frame dump'):
        print('{}:\n\tlocals={}\n\tglobals={}\n\tcells={}'
              .format(assignment, self.locals, self.globals, self.cells))


class Function(object):
    __slots__ = ['__name__', '__annotations__', '__dict__', '__doc__']

    def __init__(self, name, code, vm, pos_defaults, kw_defaults,
                 annotations, closure):
        self.__name__ = name
        self.__annotations__ = annotations
        self.__dict__ = {}
        self.__doc__ = code.co_consts[0] if code.co_consts else None

        self.code = code
        self.vm = vm
        self.pos_defaults = pos_defaults
        self.kw_defaults = kw_defaults
        self.closure = closure

        func_obj_closure = tuple(
            self.make_cell(0) for _ in self.closure
        )
        self.func_obj = types.FunctionType(code,
                                           vm.frame.globals,
                                           closure=func_obj_closure)
        self.func_obj.__name__ = self.__name__
        self.func_obj.__defaults__ = pos_defaults
        self.func_obj.__kwdefaults__ = kw_defaults
        self.func_obj.__annotations__ = annotations
        self.func_obj.__dict__ = {}

    def __call__(self, *args, **kwargs):
        args_to_frame = inspect.getcallargs(self.func_obj, *args, **kwargs)
        for key in args_to_frame:
            list_comp_magic_word = 'implicit'
            if key.startswith(list_comp_magic_word):
                new_key = key.replace(list_comp_magic_word, '.')
                args_to_frame[new_key] = args_to_frame[key]
                del args_to_frame[key]

        func_frame = self.vm.make_frame(self.code, args_to_frame)
        func_return = self.vm.run_frame(func_frame)
        return func_return

    def make_cell(self, value):
        fn = (lambda x: lambda: x)(value)
        return fn.__closure__[0]


class Cell(object):
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class VirtualMachine(object):
    def __init__(self):
        self.frame_stack = []
        self.frame = None

    def push_frame(self, frame):
        self.frame_stack.append(frame)
        self.frame = frame

    def pop_frame(self):
        self.frame_stack.pop()
        if self.frame_stack:
            self.frame = self.frame_stack[-1]
        else:
            self.frame = None

    def run_code(self, code):
        if isinstance(code, str):
            code = compile(code, '<test>', 'exec')
        frame = self.make_frame(code, args={})
        self.run_frame(frame)

    def make_frame(self, code, args):
        if not self.frame:
            locals = globals = {
                '__builtins__': __builtins__,
                '__name__': '__main__',
                '__doc__': None,
                '__package__': None
            }
            new_frame = Frame(code=code,
                              locals=locals,
                              globals=globals,
                              prev_frame=None)
            return new_frame

        new_globals = self.frame.globals
        new_globals.update(self.frame.locals)
        new_frame = Frame(code=code, locals=args, globals=new_globals,
                          prev_frame=self.frame)
        return new_frame

    def run_frame(self, frame):
        self.push_frame(frame)
        instructions = dis.get_instructions(self.frame.code)
        self.frame.init_instruction_set(instructions)

        while self.frame.ip < len(self.frame.instruction_set):
            instr = self.frame.instruction_set[self.frame.ip]
            if not instr:
                self.frame.ip += 1
                continue
            opname = instr.opname
            if opname.startswith('INPLACE'):
                opname = opname.replace('INPLACE', 'BINARY')
            method = getattr(self, opname)
            # print('HELLO! {}: {}'.format(instr.opname, instr.argval))
            method_report = method(instr)
            if method_report == 'return':
                break
            self.frame.ip += 1

        frame_return = self.frame_stack.pop()
        self.pop_frame()
        return frame_return

    def STORE_NAME(self, instr):
        self.frame.locals[instr.argval] = self.frame.stack.pop()

    def STORE_FAST(self, instr):
        self.frame.locals[instr.argval] = self.frame.stack.pop()

    def STORE_GLOBAL(self, instr):
        self.frame.globals[instr.argval] = self.frame.stack.pop()

    def STORE_SUBSCR(self, instr):
        third, second, first = self.frame.stack[-3:]
        second[first] = third

    def STORE_ATTR(self, instr):
        name = instr.argval
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        first.__dict__[name] = second
        self.frame.stack.append(second)
        self.frame.stack.append(first)

    def STORE_DEREF(self, instr):
        name = instr.argval
        value = self.frame.stack.pop()
        self.frame.cells[name].set(value)

    def SETUP_ANNOTATIONS(self, instr):
        if '__annotations__' not in self.frame.locals:
            self.frame.locals['__annotations__'] = {}

    def STORE_ANNOTATION(self, instr):
        name = instr.argval
        tos = self.frame.stack.pop()
        self.frame.locals['__annotations__'][name] = tos

    def LOAD_CONST(self, instr):
        self.frame.stack.append(instr.argval)

    def LOAD_NAME(self, instr):
        name = instr.argval
        if name in self.frame.locals:
            self.frame.stack.append(self.frame.locals[name])
        elif name in self.frame.globals:
            self.frame.stack.append(self.frame.globals[name])
        elif name in self.frame.builtins:
            self.frame.stack.append(self.frame.builtins[name])

    def LOAD_FAST(self, instr):
        name = instr.argval
        self.frame.stack.append(self.frame.locals[name])

    def LOAD_GLOBAL(self, instr):
        name = instr.argval
        if name in self.frame.globals:
            self.frame.stack.append(self.frame.globals[name])
        else:
            self.frame.stack.append(self.frame.builtins[name])

    def LOAD_ATTR(self, instr):
        name = instr.argval
        tos = self.frame.stack.pop()
        self.frame.stack.append(getattr(tos, name))

    def LOAD_CLOSURE(self, instr):
        name = instr.argval
        self.frame.stack.append(self.frame.cells[name])

    def LOAD_DEREF(self, instr):
        name = instr.argval
        self.frame.stack.append(self.frame.cells[name].get())

    def LOAD_CLASSDEREF(self, instr):
        name = instr.argval
        if name in self.frame.locals:
            self.frame.stack.append(self.frame.locals[name])
        else:
            self.frame.stack.append(self.frame.cells[name].get())

    def LOAD_BUILD_CLASS(self, instr):
        build_class_func = builtins.__build_class__
        self.frame.stack.append(build_class_func)

    def DELETE_ATTR(self, instr):
        name = instr.argval
        tos = self.frame.stack.pop()
        del tos.__dict__[name]
        self.frame.stack.append(tos)

    def DELETE_FAST(self, instr):
        name = instr.argval
        del self.frame.locals[name]

    def DELETE_GLOBAL(self, instr):
        name = instr.argval
        del self.frame.globals[name]

    def DELETE_NAME(self, instr):
        name = instr.argval
        if name in self.frame.locals:
            del self.frame.locals[name]
        else:
            del self.frame.globals[name]

    def DELETE_SUBSCR(self, instr):
        name = instr.argval
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        del second[first]
        self.frame.stack.append(second)
        self.frame.stack.append(first)

    def DELETE_DEREF(self, instr):
        name = instr.argval
        del self.frame.cells[name]

    def UNARY_POSITIVE(self, instr):
        tos = self.frame.stack.pop()
        self.frame.stack.append(+tos)

    def UNARY_NEGATIVE(self, instr):
        tos = self.frame.stack.pop()
        self.frame.stack.append(-tos)

    def UNARY_NOT(self, instr):
        tos = self.frame.stack.pop()
        self.frame.stack.append(not tos)

    def UNARY_INVERT(self, instr):
        tos = self.frame.stack.pop()
        self.frame.stack.append(~tos)

    def BINARY_POWER(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second ** first)

    def BINARY_MULTIPLY(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second * first)

    def BINARY_MATRIX_MULTIPLY(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second @ first)

    def BINARY_FLOOR_DIVIDE(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second // first)

    def BINARY_TRUE_DIVIDE(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second / first)

    def BINARY_MODULO(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second % first)

    def BINARY_ADD(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second + first)

    def BINARY_SUBTRACT(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second - first)

    def BINARY_SUBSCR(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second[first])

    def BINARY_LSHIFT(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second << first)

    def BINARY_RSHIFT(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second >> first)

    def BINARY_AND(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second & first)

    def BINARY_XOR(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second ^ first)

    def BINARY_OR(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second | first)

    def DUP_TOP(self, instr):
        tos = self.frame.stack.pop()
        self.frame.stack.append(tos)
        self.frame.stack.append(tos)

    def DUP_TOP_TWO(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(second)
        self.frame.stack.append(first)
        self.frame.stack.append(second)
        self.frame.stack.append(first)

    def POP_TOP(self, instr):
        self.frame.stack.pop()

    def ROT_TWO(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(first)
        self.frame.stack.append(second)

    def ROT_THREE(self, instr):
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        third = self.frame.stack.pop()
        self.frame.stack.append(first)
        self.frame.stack.append(third)
        self.frame.stack.append(second)

    def COMPARE_OP(self, instr):
        op = self.frame.operators[instr.argval]
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        self.frame.stack.append(op(second, first))

    def POP_JUMP_IF_FALSE(self, instr):
        tos = self.frame.stack.pop()
        if not tos:
            self.frame.ip = instr.argval - 1

    def POP_JUMP_IF_TRUE(self, instr):
        tos = self.frame.stack.pop()
        if tos:
            self.frame.ip = instr.argval - 1

    def JUMP_IF_TRUE_OR_POP(self, instr):
        tos = self.frame.stack.pop()
        if tos:
            self.frame.stack.append(tos)
            self.frame.ip = instr.argval - 1

    def JUMP_IF_FALSE_OR_POP(self, instr):
        tos = self.frame.stack.pop()
        if not tos:
            self.frame.stack.append(tos)
            self.frame.ip = instr.argval - 1

    def JUMP_ABSOLUTE(self, instr):
        self.frame.ip = instr.argval - 1

    def JUMP_FORWARD(self, instr):
        self.frame.ip = instr.argval - 1

    def FOR_ITER(self, instr):
        tos = self.frame.stack.pop()
        try:
            next = tos.__next__()
            self.frame.stack.append(tos)
            self.frame.stack.append(next)
        except StopIteration:
            self.frame.ip = instr.argval - 1

    def GET_ITER(self, instr):
        tos = self.frame.stack.pop()
        self.frame.stack.append(iter(tos))

    def BUILD_LIST(self, instr):
        num_items = instr.argval
        if num_items == 0:
            lst = []
        else:
            lst = self.frame.stack[-num_items:]
            del self.frame.stack[-num_items:]
        self.frame.stack.append(lst)

    def BUILD_LIST_UNPACK(self, instr):
        num_items = instr.argval
        res_lst = []
        if num_items == 0:
            lst_of_iterables = []
        else:
            lst_of_iterables = self.frame.stack[-num_items:]
            del self.frame.stack[-num_items:]
        for iterable in lst_of_iterables:
            res_lst += [*iterable]
        self.frame.stack.append(res_lst)

    def BUILD_TUPLE(self, instr):
        self.BUILD_LIST(instr)
        self.frame.stack[-1] = tuple(self.frame.stack[-1])

    def BUILD_TUPLE_UNPACK(self, instr):
        self.BUILD_LIST_UNPACK(instr)
        self.frame.stack[-1] = tuple(self.frame.stack[-1])

    def BUILD_TUPLE_UNPACK_WITH_CALL(self, instr):
        self.BUILD_TUPLE_UNPACK(instr)

    def BUILD_SET(self, instr):
        self.BUILD_LIST(instr)
        self.frame.stack[-1] = set(self.frame.stack[-1])

    def BUILD_SET_UNPACK(self, instr):
        self.BUILD_LIST_UNPACK(instr)
        self.frame.stack[-1] = set(self.frame.stack[-1])

    def BUILD_MAP(self, instr):
        num_items = instr.argval
        dct = {}
        for i in range(num_items):
            value = self.frame.stack.pop()
            key = self.frame.stack.pop()
            dct[key] = value
        self.frame.stack.append(dct)

    def BUILD_CONST_KEY_MAP(self, instr):
        keys = self.frame.stack.pop()
        dct = {}
        for key in reversed(keys):
            value = self.frame.stack.pop()
            dct[key] = value
        self.frame.stack.append(dct)

    def BUILD_MAP_UNPACK(self, instr):
        num_items = instr.argval
        lst_of_maps = self.frame.stack[-num_items:]
        del self.frame.stack[-num_items:]
        res_dct = {}
        for map in lst_of_maps:
            res_dct.update(map)
        self.frame.stack.append(res_dct)

    def UNPACK_SEQUENCE(self, instr):
        num_to_unpack = instr.argval
        sequence = self.frame.stack.pop()
        self.frame.stack += list(reversed(sequence))

    def UNPACK_EX(self, instr):
        lst_to_unpack = list(self.frame.stack.pop())
        lst_to_unpack[:] = lst_to_unpack[-1::-1]
        num_after_list = instr.argval // 256
        num_before_list = instr.argval % 256
        num_in_list = len(lst_to_unpack) - num_after_list - num_before_list

        self.frame.stack += lst_to_unpack[:num_after_list]
        lst = lst_to_unpack[num_after_list:num_after_list + num_in_list]
        lst[:] = lst[-1::-1]
        self.frame.stack.append(lst)
        self.frame.stack += lst_to_unpack[-num_before_list:]

    def BUILD_SLICE(self, instr):
        num_args = instr.argval
        if num_args == 2:
            first, second = reversed(self.frame.stack[-2:])
            del self.frame.stack[-2:]
            self.frame.stack.append(slice(second, first))
        if num_args == 3:
            first, second, third = reversed(self.frame.stack[-3:])
            del self.frame.stack[-3:]
            self.frame.stack.append(slice(third, second, first))

    def BUILD_STRING(self, instr):
        num_strings = instr.argval
        res_str = ''.join(self.frame.stack[-num_strings:])
        del self.frame.stack[-num_strings:]
        self.frame.stack.append(res_str)

    def LIST_APPEND(self, instr):
        count = instr.argval
        tos = self.frame.stack.pop()
        list.append(self.frame.stack[-count], tos)

    def SET_ADD(self, instr):
        count = instr.argval
        tos = self.frame.stack.pop()
        set.add(self.frame.stack[-count], tos)

    def MAP_ADD(self, instr):
        count = instr.argval
        key = self.frame.stack.pop()
        value = self.frame.stack.pop()
        dest = self.frame.stack[-count]
        dest[key] = value

    def SETUP_LOOP(self, instr):
        block_params = {'begin': instr.offset,
                        'end': instr.argval}
        self.frame.block_stack.append(block_params)

    def BREAK_LOOP(self, instr):
        loop_block = self.frame.block_stack.pop()
        self.frame.ip = loop_block['end'] - 1

    def CONTINUE_LOOP(self, instr):
        self.frame.ip = instr.argval - 1

    def POP_BLOCK(self, instr):
        self.frame.block_stack.pop()

    def MAKE_FUNCTION(self, instr):
        flag = instr.argval

        func_name = self.frame.stack.pop()
        func_code = self.frame.stack.pop()

        closure = ()
        if flag >= 8:
            closure = self.frame.stack.pop()
            flag -= 8

        annotations = {}
        if flag >= 4:
            annotations = self.frame.stack.pop()
            flag -= 4

        kw_defaults = {}
        if flag >= 2:
            kw_defaults = self.frame.stack.pop()
            flag -= 2

        pos_defaults = ()
        if flag >= 1:
            pos_defaults = self.frame.stack.pop()
            flag -= 1

        func = Function(name=func_name,
                        code=func_code,
                        vm=self,
                        pos_defaults=pos_defaults,
                        kw_defaults=kw_defaults,
                        annotations=annotations,
                        closure=closure)
        self.frame.stack.append(func)

    def CALL_FUNCTION(self, instr):
        num_args = instr.argval
        args = []
        for i in range(num_args):
            args.append(self.frame.stack.pop())
        func = self.frame.stack.pop()
        if func == builtins.__build_class__:
            args[-1] = args[-1].func_obj
        res = func(*reversed(args))
        self.frame.stack.append(res)

    def CALL_FUNCTION_KW(self, instr):
        total_num_args = instr.argval
        kwarg_names = self.frame.stack.pop()

        num_kwargs = len(kwarg_names)
        kwargs_values = self.frame.stack[-num_kwargs:]
        del self.frame.stack[-num_kwargs:]
        kwargs = {key: value
                  for (key, value)
                  in zip(kwarg_names, kwargs_values)}

        num_posargs = total_num_args - num_kwargs
        if num_posargs:
            posargs = self.frame.stack[-num_posargs:]
            del self.frame.stack[-num_posargs:]
        else:
            posargs = []

        func = self.frame.stack.pop()
        res = func(*posargs, **kwargs)
        self.frame.stack.append(res)

    def CALL_FUNCTION_EX(self, instr):
        kw_present = instr.argval
        kwargs = {}
        if kw_present:
            kwargs = self.frame.stack.pop()
        posargs = self.frame.stack.pop()
        func = self.frame.stack.pop()
        func_res = func(*posargs, **kwargs)
        self.frame.stack.append(func_res)

    def RETURN_VALUE(self, instr):
        return_value = self.frame.stack.pop()
        self.frame_stack.append(return_value)
        return 'return'

    def IMPORT_NAME(self, instr):
        name = instr.argval
        first = self.frame.stack.pop()
        second = self.frame.stack.pop()
        module = __import__(name=name, fromlist=first, level=second)
        self.frame.stack.append(module)

    def IMPORT_FROM(self, instr):
        name = instr.argval
        module = self.frame.stack[-1]
        attr = getattr(module, name)
        self.frame.stack.append(attr)

    def IMPORT_STAR(self, instr):
        module = self.frame.stack.pop()
        for name in module.__dict__:
            if name.startswith('_'):
                continue
            symbol = getattr(module, name)
            self.frame.locals[name] = symbol

    def EXTENDED_ARG(self, instr):
        pass

    def POP_EXCEPT(self, instr):
        pass

    def RAISE_VARARGS(self, instr):
        num_args = instr.argval
        if num_args == 1:
            first = self.frame.stack.pop()
            raise first
        elif num_args == 2:
            first = self.frame.stack.pop()
            second = self.frame.stack.pop()
            raise first(second)
        elif num_args == 3:
            first = self.frame.stack.pop()
            second = self.frame.stack.pop()
            third = self.frame.stack.pop()
            raise first(second).with_traceback(third)
        else:
            raise


if __name__ == '__main__':
    vm = VirtualMachine()
    run_vm(vm)
