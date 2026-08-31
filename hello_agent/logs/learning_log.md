## 2026-08-25 — API Response Debugging

### Problem

for search tool: I initially printed the entire SerpApi response with `print(result)`.
The output was too large and difficult to understand.

### Better Approach

Inspect the response structure first with `type(result)` and `result.keys()`.
Then inspect only the relevant nested fields, such as `organic_results`.

### Why It Helps

This makes unfamiliar API responses easier to understand and debug.
It also prevents guessing field names before writing parsing logic.

### Key Takeaway

**Structure first, values second.**
Use `type() → keys() → nested keys → values → parser`.


### Problem

I was trying to understand fields like answer_box, knowledge_graph, and organic_results only by printing API responses.
This works, but some fields may not appear in every search result.

### Better Approach

Check the official API documentation first to understand the response schema and possible fields.
Then use result.keys() and nested keys() to inspect the actual response returned by my query.

### Why It Helps

Official documentation shows what the API can return, while print() helps verify what it returned in a specific request.
This prevents guessing field names or relying on one example response.

### Key Takeaway

Docs first, inspect second, code third.
Understand the API schema → inspect the real response → write the parser.

## 2026-08-27

### Problem

After adding `description`, each tool was no longer stored as a function directly.  
Each tool `name` now points to a dictionary containing both `description` and `func`.

### Why It Broke

`getTool()` originally only retrieved the value under `name`.  
After the structure changed, that value became the whole tool information dictionary instead of the function itself.

### Better Approach

The retrieval path now needs two steps:  
tool `name` → tool information dictionary → `func`.

### My Version vs Safer Version

`self.tools.get(name).get("func")` works if `name` definitely exists.  
If `name` does not exist, the first `.get(name)` returns `None`, so calling `.get("func")` on `None` causes an error.

`self.tools.get(name, {}).get("func")` is safer.  
If `name` does not exist, it returns an empty dictionary first, and the second `.get("func")` simply returns `None`.

### Key Takeaway

When data becomes nested, retrieval must follow the same nested structure.  
For chained `.get()`, provide a safe default value when the next step still expects a dictionary.

## 2026-08-31

### Problem

I needed to parse the LLM's ReAct output into `Thought` and `Action`, and then further extract the action name and input.

### My Version

I first tested several real LLM responses and observed that the output format was relatively stable.

Based on that actual structure, I wrote a simpler parser that relies on the final non-empty `Thought` and `Action` lines, with lightweight regex/string operations for extraction.

This version is easier for me to understand, debug, and modify.

### Tutorial Version

The tutorial uses a more general regex-based parser.

Instead of relying on fixed line positions, it matches the `Thought:` and `Action:` patterns directly and can better handle cases such as multi-line content or slightly less stable formatting.

It also includes safer fallback behavior when the expected format is not matched.

### My Version vs Tutorial Version

My version is more targeted to the response format I actually observed during testing.

The tutorial version is more robust and general, but also more complex because it relies more heavily on regular expressions.

For the current stage, I prefer to keep my simpler version because it already works with the tested responses and makes the parsing logic easier to understand.

If later tests reveal format changes, multi-line parsing issues, or parsing errors, I can then upgrade the relevant parts toward the more general regex version.

### Key Takeaway

A parser does not need to be maximally general from the beginning.

It is reasonable to start with a simple implementation based on observed output patterns, verify it with multiple real responses, and only add more robust regex handling when an actual failure case appears.