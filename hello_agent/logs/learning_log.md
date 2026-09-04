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

## 2026-09-01

# ReAct Agent Debugging Log

## 1. Parser Relied on Fixed Line Positions

### Problem

The first version of `_parse_output()` assumed that the last two non-empty lines of every LLM response were always:

* `Thought`
* `Action`

It therefore parsed the response using positions such as `part[-2]` and `part[-1]`.

This worked for simple responses, but failed once the model produced additional lines.

### Better Approach

Parse the response based on explicit labels such as `Thought:` and `Action:` instead of their positions.

Search the whole response for the corresponding fields rather than assuming where they appear.

### Why It Helps

LLM output length is not always stable.

Using semantic markers is more robust than relying on fixed line positions because additional text does not automatically break the parser.

### Key Takeaway

**Parse by structure, not by position.**

`Thought:` / `Action:` are more reliable signals than `part[-2]` / `part[-1]`.

---

## 2. Multi-line `Finish[...]` Could Not Be Parsed Completely

### Problem

The parser originally used:

```python
re.search(r"Action:\s*(.*)", text)
```

This worked when the final answer was on one line:

```text
Action: Finish[The answer is ...]
```

However, longer final answers were often formatted across multiple lines:

```text
Action: Finish[
line 1
line 2
line 3
]
```

Since `.` does not match newline characters by default, only the first line of the final answer was extracted.

### Better Approach

Handle `Finish[...]` separately and allow the regular expression to match across multiple lines:

```python
if "Action: Finish" in text:
    action_match = re.search(
        r"Action:\s*(Finish\[.*?\])",
        text,
        re.DOTALL
    )
else:
    action_match = re.search(
        r"Action:\s*(.*)",
        text
    )
```

`re.DOTALL` allows `.` to match newline characters, so the whole `Finish[...]` block can be captured.

### Why It Helps

Tool actions such as `search[...]` are usually short and single-line, while final answers may be much longer.

Handling the two cases differently keeps the simple parser while supporting realistic multi-line answers.

### Key Takeaway

**Different Action types may require different parsing strategies.**

Single-line tool calls can use simple parsing, while multi-line final answers need explicit multi-line support.

---

## 3. `history` Was Updated but Never Sent Back to the LLM

### Problem

The ReAct loop successfully accumulated previous steps:

```python
history += ...
```

but the prompt was still constructed with:

```python
history=""
```

As a result, the next LLM call could not see the previous:

* Thought
* Action
* Observation

The loop existed, but the model effectively started from scratch every time.

### Better Approach

Pass the real history back into the prompt:

```python
prompt = REACT_PROMPT_TEMPLATE.format(
    tools=tools,
    question=question,
    history=history
)
```

After each tool call, append the complete interaction:

```text
Thought
Action
Observation
```

to `history`.

### Why It Helps

The Observation is what allows the next reasoning step to use information returned by the tool.

Without history, the program has a loop, but it does not have a meaningful ReAct loop.

The actual flow should be:

```text
Thought
→ Action
→ Tool
→ Observation
→ History
→ Next Thought
```

### Key Takeaway

**A loop alone does not create an Agent.**

ReAct requires previous tool results to be fed back into the model.

---

## 4. LLM Occasionally Returned `None`

### Problem

During multi-step execution, some LLM calls returned no usable response.

In one case, the provider explicitly returned an error such as:

```text
Service temporarily overloaded
```

The existing `llm_client.py` caught the exception and returned:

```python
None
```

which caused the Agent to terminate.

### Better Approach

The problem was not in the ReAct loop itself but in the stability of the free LLM provider.

Instead of immediately rewriting the LLM client or Agent logic, test another fixed model/provider.

Keeping the model fixed is also better for debugging than using a router that may select different free models between calls.

### Why It Helps

When debugging an Agent, too many changing components make failures difficult to locate.

A more stable fixed model reduces uncertainty between:

* Agent logic errors
* Parser errors
* Prompt problems
* Provider failures

### Key Takeaway

**Separate infrastructure failures from Agent logic failures.**

If the provider is unstable, changing the model may be more appropriate than changing working Agent code.

---

## 5. "Latest News" Search Returned 2024 Information

### Problem

When the user asked for the latest OpenAI news, the Agent generated queries such as:

```text
search["OpenAI latest news 2024"]
```

The search tool correctly followed the query and therefore returned mostly 2024 information.

The problem was not necessarily the search tool itself.

The LLM did not know the real current date and inserted an outdated year into the query.

### Better Approach

Provide the current date as runtime context instead of hard-coding it manually.

For example:

```python
from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")
```

Then inject it into the prompt:

```python
prompt = REACT_PROMPT_TEMPLATE.format(
    tools=tools,
    current_date=current_date,
    question=question,
    history=history
)
```

The prompt also explicitly tells the Agent:

```text
For questions asking for the latest or current information:
- Use the current date when forming search queries.
- Prefer authoritative and official sources when available.
```

Additional prompt instructions were added to make the ReAct execution boundary clearer:

```text
Output exactly one Thought and one Action per turn.
After outputting Action, stop.
Do not generate Observation yourself.
Observation will be provided after the tool is executed.
```

After adding the date information, the Agent correctly generated queries such as:

```text
search["OpenAI latest news September 2026"]
```

and retrieved recent 2026 results.

### Why It Helps

A search tool can only search according to the query it receives.

If the Agent creates a query containing an incorrect year, even a correctly functioning search tool may return outdated information.

Providing environment context helps the Agent construct better tool inputs.

The explicit prompt rules also make the responsibilities clearer:

```text
LLM → Thought + Action
Tool → Observation
LLM → Next Thought / Finish
```

### Key Takeaway

**Tool quality is only one part of Agent quality.**

The Agent must also have enough context to generate the correct tool input.

For time-sensitive questions:

```text
Current runtime context
→ Better query
→ Better Observation
→ Better final answer
```

---

## 6. Old Parser Tests Broke After `run()` Took Over Parsing

### Problem

Initially, `run()` only returned the raw LLM response.

The external test therefore manually executed:

```python
think, action = agent._parse_output(response)
tool_name, tool_action = agent._parse_action(action)
```

Later, parsing and tool execution were moved inside `run()`.

At that point, `run()` could return an Observation or final answer instead of the original:

```text
Thought: ...
Action: ...
```

The old test still tried to parse the returned result again, which caused errors such as `IndexError`.

### Better Approach

Update the test whenever the responsibility of the function changes.

After `run()` became responsible for the complete Agent loop, the integration test only needed to check:

```python
result = agent.run(question)
print(result)
```

Parser functions can still be tested separately using controlled example responses.

### Why It Helps

There are now two different types of tests:

```text
Parser Test
Fake LLM response
→ _parse_output()
→ _parse_action()
```

and:

```text
Agent Integration Test
Question
→ run()
→ Final result
```

Keeping these responsibilities separate avoids processing the same data twice.

### Key Takeaway

**When a function's responsibility changes, its tests must change with it.**

Test internal parsers separately and test `run()` as the complete Agent workflow.

##  2026-09-04

## 1. Converting the Plan from `str` to `list`

### Problem

The Planner successfully generated a structured plan, but the LLM response was still returned as a string.

For example:

````text
```python
["step 1", "step 2", "step 3"]
````

````

Although the content looks like a Python list, its actual type is still:

```python
str
````

This creates a problem for the Executor because it needs to process each plan step separately.

If the plan remains a string, iterating over it would process individual characters instead of complete steps.

### Better Approach

First extract the list content from the Markdown code block:

````python
plan_str = response.split("```python")[1].split("```")[0].strip()
````

Then convert the list-like string into a real Python list:

```python
plan = ast.literal_eval(plan_str)
```

The result becomes:

```python
["step 1", "step 2", "step 3"]
```

with type:

```python
list
```

### Why It Helps

The Executor can now iterate through the plan step by step:

```python
for step in plan:
```

Each `step` represents one complete task instead of one character from the original string.

This also makes the Planner output easier to use as structured data in later Agent components.

### Key Takeaway

**LLM output may look structured without actually being structured data.**

Convert the model output into the correct Python data type before passing it to later components.

---

## 2. Plan-and-Solve Cannot Perform Real Search Without Tools

### Problem

The first Plan-and-Solve test asked the Agent to research the latest developments in AI agents.

The Planner successfully generated steps such as:

```text
Collect recent publications
Analyze recent developments
Summarize the main trends
```

The Executor also completed each step without errors.

However, the Executor currently only executes:

```python
self.llm.think(...)
```

It has no search tool or external retrieval capability.

As a result, when the plan asks the Executor to "search" or "collect recent information", the LLM only generates an answer from its existing knowledge instead of actually searching external sources.

### Better Approach

Do not treat this as a failure of the Plan-and-Solve loop itself.

First test the baseline with a task that does not require external tools.

For example, an arithmetic reasoning problem was used instead:

```text
Monday: 15 apples
Tuesday: twice Monday
Wednesday: 5 fewer than Tuesday
```

The Planner generated the steps correctly, the Executor processed them sequentially, and the final answer was:

```text
70
```

This confirmed that the core Plan-and-Solve workflow was working correctly.

Real search capability can be added later by integrating tools into the Executor.

### Why It Helps

Separating the Agent workflow from tool capability makes debugging easier.

It helps distinguish between:

* Planner errors

* Executor loop errors

* History propagation errors

* Missing external tools

A task may require search, but that does not mean the planning or execution framework itself is broken.

### Key Takeaway

**A step that says "search" does not mean the Agent actually searched.**

Without a real search tool, the Executor only asks the LLM to generate an answer based on its existing knowledge.

