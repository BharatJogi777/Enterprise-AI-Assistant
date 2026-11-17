import ast
import operator
from datetime import datetime, timezone
from langchain_core.tools import tool
from enterprise_ai.services.rag import search_documents
from enterprise_ai.services.web_search import search_web

_ALLOWED = {ast.Add:operator.add, ast.Sub:operator.sub, ast.Mult:operator.mul,
            ast.Div:operator.truediv, ast.FloorDiv:operator.floordiv,
            ast.Mod:operator.mod, ast.Pow:operator.pow, ast.USub:operator.neg,
            ast.UAdd:operator.pos}

def _calculate(node):
    if isinstance(node, ast.Expression):
        return _calculate(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int,float):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED:
        return _ALLOWED[type(node.op)](_calculate(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED:
        left,right = _calculate(node.left),_calculate(node.right)
        if isinstance(node.op,ast.Pow) and abs(right)>8:
            raise ValueError("Exponent is outside allowed bounds")
        result = _ALLOWED[type(node.op)](left,right)
        if abs(result)>1e15:
            raise ValueError("Result is outside allowed bounds")
        return result
    raise ValueError("Only basic arithmetic expressions are allowed")

@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression."""
    try:
        return str(_calculate(ast.parse(expression,mode="eval")))
    except (SyntaxError,ValueError,ZeroDivisionError,OverflowError) as exc:
        return f"Calculation rejected: {exc}"

@tool
def utc_time() -> str:
    """Return the current UTC date and time."""
    return datetime.now(timezone.utc).isoformat()

@tool
async def search_internal_documents(query: str) -> str:
    """Search indexed internal company documents and return matching excerpts."""
    rows = await search_documents(query,top_k=4)
    if not rows:
        return "No matching internal document excerpts were found."
    return "\n\n".join(
        f"Source: {x['filename']} (chunk {x['chunk_index']}, similarity {float(x['similarity']):.3f})\n{x['content']}"
        for x in rows)

@tool
async def search_web_tool(query: str) -> str:
    """Search the public web for current information; report source titles and URLs."""
    rows = await search_web(query,limit=5)
    if not rows:
        return "The configured search provider returned no results."
    return "\n\n".join(f"Title: {x['title']}\nURL: {x['url']}\nSnippet: {x['snippet']}"
                         for x in rows)

BUILTIN_TOOLS = {x.name:x for x in
                 [calculator,utc_time,search_internal_documents,search_web_tool]}
