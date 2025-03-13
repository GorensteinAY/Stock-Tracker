# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/12_py2pyi.ipynb.

# %% auto 0
__all__ = ['functypes', 'imp_mod', 'has_deco', 'sig2str', 'ast_args', 'create_pyi', 'py2pyi', 'replace_wildcards']

# %% ../nbs/12_py2pyi.ipynb
import ast, sys, inspect, re, os, importlib.util, importlib.machinery

from ast import parse, unparse
from inspect import signature, getsource
from .utils import *
from .meta import delegates

# %% ../nbs/12_py2pyi.ipynb
def imp_mod(module_path, package=None):
    "Import dynamically the module referenced in `fn`"
    module_path = str(module_path)
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    spec = importlib.machinery.ModuleSpec(module_name, None, origin=module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader = importlib.machinery.SourceFileLoader(module_name, module_path)
    if package is not None: module.__package__ = package
    module.__file__ = os.path.abspath(module_path)
    spec.loader.exec_module(module)
    return module

# %% ../nbs/12_py2pyi.ipynb
def _get_tree(mod):
    return parse(getsource(mod))

# %% ../nbs/12_py2pyi.ipynb
@patch
def __repr__(self:ast.AST):
    return unparse(self)

@patch
def _repr_markdown_(self:ast.AST):
    return f"""```python
{self!r}
```"""

# %% ../nbs/12_py2pyi.ipynb
functypes = (ast.FunctionDef,ast.AsyncFunctionDef)

# %% ../nbs/12_py2pyi.ipynb
def _deco_id(d:Union[ast.Name,ast.Attribute])->bool:
    "Get the id for AST node `d`"
    return d.id if isinstance(d, ast.Name) else d.func.id

def has_deco(node:Union[ast.FunctionDef,ast.AsyncFunctionDef], name:str)->bool:
    "Check if a function node `node` has a decorator named `name`"
    return any(_deco_id(d)==name for d in getattr(node, 'decorator_list', []))

# %% ../nbs/12_py2pyi.ipynb
def _get_proc(node):
    if isinstance(node, ast.ClassDef): return _proc_class
    if not isinstance(node, functypes): return None
    if not has_deco(node, 'delegates'): return _proc_body
    if has_deco(node, 'patch'): return _proc_patched
    return _proc_func

# %% ../nbs/12_py2pyi.ipynb
def _proc_tree(tree, mod):
    for node in tree.body:
        proc = _get_proc(node)
        if proc: proc(node, mod)

# %% ../nbs/12_py2pyi.ipynb
def _clean_patched_node(node):
    "Clean the patched node in-place."
    # When moving a patched node to its parent, we no longer need the patch decorator and parent annotation.
    node.decorator_list = [deco for deco in node.decorator_list if getattr(deco, "id", None) != "patch"]
    node.args.args[0].annotation = None

# %% ../nbs/12_py2pyi.ipynb
def _is_empty_class(node):
    if not isinstance(node, ast.ClassDef): return False
    if len(node.body) != 1: return False
    child = node.body[0]
    if isinstance(child, ast.Pass): return True
    if isinstance(child, ast.Expr) and isinstance(child.value, (ast.Ellipsis, ast.Str)): return True
    return False

# %% ../nbs/12_py2pyi.ipynb
def _add_patched_node_to_parent(node, parent):
    "Add a patched node to its parent."
    # if the patch node updates an existing class method, let's replace it.
    for i, child in enumerate(parent.body):
        if hasattr(child, "name") and child.name == node.name:
            parent.body[i] = node
            return
    # if we've made it this far the patched node must be new, so we append it to the parent's list of children
    if _is_empty_class(parent): parent.body = [node]
    else: parent.body.append(node)

# %% ../nbs/12_py2pyi.ipynb
def _proc_patches(tree, mod):
    "Move all patched methods to their parents."
    class_nodes = {}  # {class_name: position in node tree}
    i = 0
    while i < len(tree.body):
        node = tree.body[i]
        if isinstance(node, ast.ClassDef):
            # patched nodes can access their parent using different scopes:
            #  - local scope (e.g. self: A)
            #  - modular scope (e.g. self: example.A) [used by @delegates]
            class_nodes.update({node.name: i, f"{mod.__name__}.{node.name}": i})
        elif isinstance(node, ast.FunctionDef) and has_deco(node, "patch"):
            annotation = node.args.args[0].annotation
            # a patched node can have 1 or more parents
            parents = annotation.elts if hasattr(annotation, "elts") else [annotation]
            parents = list(map(str, parents))
            parents_in_mod = [parent for parent in parents if parent in class_nodes]
            # we can move the patched node if at least one parent lives in the current module
            if parents_in_mod:
                _clean_patched_node(node)
                for parent in parents_in_mod:
                    parent_node = tree.body[class_nodes[parent]]
                    _add_patched_node_to_parent(node, parent_node)
                tree.body.pop(i)
                i -= 1  # as we've removed the patched node from the tree we need to decrement the loop counter
        i += 1

# %% ../nbs/12_py2pyi.ipynb
def _proc_mod(mod):
    tree = _get_tree(mod)
    _proc_tree(tree, mod)
    _proc_patches(tree, mod)
    return tree

# %% ../nbs/12_py2pyi.ipynb
def sig2str(sig):
    s = str(sig)
    s = re.sub(r"<class '(.*?)'>", r'\1', s)
    s = re.sub(r"dynamic_module\.", "", s)
    return s

# %% ../nbs/12_py2pyi.ipynb
def ast_args(func):
    sig = signature(func)
    return ast.parse(f"def _{sig2str(sig)}: ...").body[0].args

# %% ../nbs/12_py2pyi.ipynb
def _body_ellip(n: ast.AST):
    stidx = 1 if isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Str) else 0
    n.body[stidx:] = [ast.Expr(ast.Constant(...))]

# %% ../nbs/12_py2pyi.ipynb
def _update_func(node, sym):
    """Replace the parameter list of the source code of a function `f` with a different signature.
    Replace the body of the function with just `pass`, and remove any decorators named 'delegates'"""
    # sym_args contains the complete set of node args including any delegates kwargs.
    # when adding the delegates kwargs any annotation with a user-defined type is given a fully qualified name (e.g. mod.submod.func).
    # unfortunately the fully qualified names don't match the import statements in the node tree.
    # this can break downstream applications such as "jump to definition" in IDEs.
    # to resolve this issue we replace the annotations of user-defined types with the original annotations.
    sym_args = ast_args(sym)
    node_args = {arg.arg: arg.annotation for arg in node.args.args + node.args.kwonlyargs}
    for arg in sym_args.args + sym_args.kwonlyargs:
        arg.annotation = node_args.get(arg.arg, arg.annotation)
    node.args = sym_args
    _body_ellip(node)
    node.decorator_list = [d for d in node.decorator_list if _deco_id(d) != 'delegates']

# %% ../nbs/12_py2pyi.ipynb
def _proc_body(node, mod): _body_ellip(node)

# %% ../nbs/12_py2pyi.ipynb
def _proc_func(node, mod):
    sym = getattr(mod, node.name)
    _update_func(node, sym)

# %% ../nbs/12_py2pyi.ipynb
def _proc_patched(node, mod):
    ann = node.args.args[0].annotation
    if hasattr(ann, 'elts'): ann = ann.elts[0]
    cls = getattr(mod, ann.id)
    sym = getattr(cls, node.name)
    _update_func(node, sym)

# %% ../nbs/12_py2pyi.ipynb
def _proc_class(node, mod):
    cls = getattr(mod, node.name)
    _proc_tree(node, cls)

# %% ../nbs/12_py2pyi.ipynb
def create_pyi(fn, package=None):
    "Convert `fname.py` to `fname.pyi` by removing function bodies and expanding `delegates` kwargs"
    fn = Path(fn)
    mod = imp_mod(fn, package=package)
    tree = _proc_mod(mod)
    res = unparse(tree)
    fn.with_suffix('.pyi').write_text(res)

# %% ../nbs/12_py2pyi.ipynb
from .script import call_parse

# %% ../nbs/12_py2pyi.ipynb
@call_parse
def py2pyi(fname:str,  # The file name to convert
           package:str=None  # The parent package
          ):
    "Convert `fname.py` to `fname.pyi` by removing function bodies and expanding `delegates` kwargs"
    create_pyi(fname, package)

# %% ../nbs/12_py2pyi.ipynb
@call_parse
def replace_wildcards(
    # Path to the Python file to process
    path: str):
    "Expand wildcard imports in the specified Python file."
    path = Path(path)
    path.write_text(expand_wildcards(path.read_text()))
