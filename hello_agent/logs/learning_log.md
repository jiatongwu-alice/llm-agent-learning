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