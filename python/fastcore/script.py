"""A fast way to turn your python function into a script."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/08_script.ipynb.

# %% auto 0
__all__ = ['SCRIPT_INFO', 'store_true', 'store_false', 'bool_arg', 'clean_type_str', 'Param', 'anno_parser', 'args_from_prog',
           'call_parse']

# %% ../nbs/08_script.ipynb
import inspect,argparse,shutil
from functools import wraps,partial
from .imports import *
from .utils import *
from .docments import docments

# %% ../nbs/08_script.ipynb
def store_true():
    "Placeholder to pass to `Param` for `store_true` action"
    pass

# %% ../nbs/08_script.ipynb
def store_false():
    "Placeholder to pass to `Param` for `store_false` action"
    pass

# %% ../nbs/08_script.ipynb
def bool_arg(v):
    "Use as `type` for `Param` to get `bool` behavior"
    return str2bool(v)

# %% ../nbs/08_script.ipynb
def clean_type_str(x:str):
    x = str(x)
    x = re.sub(r"(enum |class|function|__main__\.|\ at.*)", '', x)
    x = re.sub(r"(<|>|'|\ )", '', x) # spl characters
    return x

# %% ../nbs/08_script.ipynb
class Param:
    "A parameter in a function used in `anno_parser` or `call_parse`"
    def __init__(self, help="", type=None, opt=True, action=None, nargs=None, const=None,
                 choices=None, required=None, default=None, version=None):
        if type in (store_true,bool):  type,action,default=None,'store_true',False
        if type==store_false: type,action,default=None,'store_false',True
        if type and isinstance(type,typing.Type) and issubclass(type,enum.Enum) and not choices: choices=list(type)
        help = help or ""
        store_attr()

    def set_default(self, d):
        if self.action == "version":
            if d != inspect.Parameter.empty: self.version = d
            self.opt = True
            return
        if self.default is None:
            if d == inspect.Parameter.empty: self.opt = False
            else: self.default = d
        if self.default is not None:
            self.help += f" (default: {self.default})"

    @property
    def pre(self): return '--' if self.opt else ''
    @property
    def kwargs(self): return {k:v for k,v in self.__dict__.items()
                              if v is not None and k!='opt' and k[0]!='_'}
    def __repr__(self):
        if not self.help and self.type is None: return ""
        if not self.help and self.type is not None: return f"{clean_type_str(self.type)}"
        if self.help and self.type is None: return f"<{self.help}>"
        if self.help and self.type is not None: return f"{clean_type_str(self.type)} <{self.help}>"

# %% ../nbs/08_script.ipynb
class _HelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog, indent_increment=2):
        cols = shutil.get_terminal_size((120,30))[0]
        super().__init__(prog, max_help_position=cols//2, width=cols, indent_increment=indent_increment)
    def _expand_help(self, action): return self._get_help_string(action)

# %% ../nbs/08_script.ipynb
def anno_parser(func,  # Function to get arguments from
                prog:str=None):  # The name of the program
    "Look at params (annotated with `Param`) in func and return an `ArgumentParser`"
    p = argparse.ArgumentParser(description=func.__doc__, prog=prog, formatter_class=_HelpFormatter)
    for k,v in docments(func, full=True, returns=False, eval_str=True).items():
        param = v.anno
        if not isinstance(param,Param): param = Param(v.docment, v.anno)
        param.set_default(v.default)
        p.add_argument(f"{param.pre}{k}", **param.kwargs)
    p.add_argument(f"--pdb", help=argparse.SUPPRESS, action='store_true')
    p.add_argument(f"--xtra", help=argparse.SUPPRESS, type=str)
    return p

# %% ../nbs/08_script.ipynb
def args_from_prog(func, prog):
    "Extract args from `prog`"
    if prog is None or '#' not in prog: return {}
    if '##' in prog: _,prog = prog.split('##', 1)
    progsp = prog.split("#")
    args = {progsp[i]:progsp[i+1] for i in range(0, len(progsp), 2)}
    annos = type_hints(func)
    for k,v in args.items():
        t = annos.get(k, Param()).type
        if t: args[k] = t(v)
    return args

# %% ../nbs/08_script.ipynb
SCRIPT_INFO = SimpleNamespace(func=None)

# %% ../nbs/08_script.ipynb
def call_parse(func=None, nested=False):
    "Decorator to create a simple CLI from `func` using `anno_parser`"
    if func is None: return partial(call_parse, nested=nested)

    @wraps(func)
    def _f(*args, **kwargs):
        mod = inspect.getmodule(inspect.currentframe().f_back)
        if not mod: return func(*args, **kwargs)
        if not SCRIPT_INFO.func and mod.__name__=="__main__": SCRIPT_INFO.func = func.__name__
        if len(sys.argv)>1 and sys.argv[1]=='': sys.argv.pop(1)
        p = anno_parser(func)
        if nested: args, sys.argv[1:] = p.parse_known_args()
        else: args = p.parse_args()
        args = args.__dict__
        xtra = otherwise(args.pop('xtra', ''), eq(1), p.prog)
        tfunc = trace(func) if args.pop('pdb', False) else func
        return tfunc(**merge(args, args_from_prog(func, xtra)))

    mod = inspect.getmodule(inspect.currentframe().f_back)
    if getattr(mod, '__name__', '') =="__main__":
        setattr(mod, func.__name__, _f)
        SCRIPT_INFO.func = func.__name__
        return _f()
    else: return _f
