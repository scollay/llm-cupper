content_prompt = """
You are a financial markets analyst writing a short reference article for an educational audience of active, knowledgeable traders. Write at the level of a clear Investopedia explainer.

Length: about 1000 words. Be concise and do not pad.

Use clean Markdown. Do not include hyperlinks, raw HTML, images, or tables. Light formatting that improves readability and organization is encouraged: subheadings within a section, bulleted or numbered lists, occasional bold or italic for genuine emphasis, and inline code (backticks) for things like column names. Use emphasis sparingly — formatting should aid the reader, not decorate the page.

The article should contain five key elements: title, overview, Details, text formula, Python code
Use this outline and these markdown headings. Keep the four "##" section headings exactly as written. Replace the "# " title line with the article's real title — the name of the indicator itself (for example, "# Relative Strength Index"); do not output the literal word "Title".

# <the indicator's name>

## Overview
A few sentences on what the indicator is, how it appears on a chart,
and who created it and when (if known).

## Details
The body of the article. Explain how the indicator works, how traders typically interpret it, and where that interpretation tends to break down.

## Text Formula
Include a formula in text format that shows how to calculate all aspects of the indicator mentioned in the article.

## Python Code
Write Python code to calculate and return all potential values of the indicator mentioned in the article.
Place all Python inside one fenced Markdown code block. Open it with a line that is exactly ```python and close it with a line that is exactly ```.
Put nothing but code and code comments inside the fence; keep all explanatory prose outside it.
Assume a Pandas Dataframe input with columns: symbol, date, open, high, low, close.
Assume that the Dataframe can contain data for one or more symbols.
Do not simulate data in an actual dataframe, just present and document the required format in the code

Use whatever process produces your best possible result — plan, draft, and revise as needed. Before finalizing, verify your own work: confirm the Python code is correct and would run without errors on a DataFrame containing one or more symbols, that it computes every value the article describes, that it handles each symbol independently, and that the code, the Text Formula, and the prose all agree. Correct anything wrong or inconsistent.
Output only the finished article: begin your response with the title (H1) line and include nothing before or after the five required sections — no planning notes, drafts, or commentary.

Write an article about {topic}.
"""

grader_prompt = """
You are an expert evaluator. You will grade one AI-generated article (CONTENT) from a writing-and-coding assignment, strictly and consistently.

You are given two things below:

1. ASSIGNMENT — the exact prompt the author model was given.
2. CONTENT — one author model's output. It begins with a metadata header (a JSON block) added automatically by the test harness; it is NOT written by the author. Read the "model" field from it and copy that id into your output as "model_code". Then ignore the header entirely: the article being graded is everything AFTER that header. Do not grade the header, do not count it toward length, and do not treat its presence or its JSON/braces as a formatting issue.

The assignment may concern ANY subject — a financial indicator, a scientific concept, any topic. Do NOT assume a particular subject. Derive the specific requirements (required sections/headings, target length, allowed formatting, required code behavior, input data format, and what the code must compute) from the ASSIGNMENT text itself, then grade the CONTENT against those requirements plus general quality. Judge only what the ASSIGNMENT requires and what the CONTENT itself claims; do not invent requirements.

== SCALE ==
Score every criterion 0-3. Use the full range; reserve 3 for genuinely excellent work and 0 for missing/wrong.
  0 = missing or wrong
  1 = present but major problems
  2 = solid, minor issues
  3 = excellent / complete

== CRITERIA ==
1. clarity — Well-organized, readable, logically sequenced writing pitched at the audience the assignment specifies. Thoughtful light formatting that aids readability and organization — subheadings, lists, and occasional emphasis where they genuinely help — counts in the article's favor; an undifferentiated wall of text counts against it, as does noisy, excessive, or decorative formatting that hurts readability.

2. accuracy — The explanation, any stated formula, and the code are factually and mathematically correct AND mutually consistent. A prose description, formula, and code that contradict one another is an accuracy failure even if each looks plausible alone. Apply your own domain expertise and name the specific error(s).

3. depth — Appropriate substance for the stated audience and length: mechanism, interpretation, and limitations/caveats where relevant. Reward genuine completeness, NOT word count or padding.

4. adherence — Follows the assignment's explicit constraints: the required headings/sections, the target length (penalize being well under or well over), output-format rules (which formatting is allowed vs. disallowed — e.g., no hyperlinks, HTML, images, or tables if specified), and the specified code input format.

5. code — Judging the code statically (you cannot run it): does it implement the method correctly and completely — computing and returning EVERY value the CONTENT describes, handling the specified input (including multiple entities/symbols if the assignment requires it), using correct statistical conventions, with no logic bugs — AND would it run without error on a valid input, accounting for runtime errors, row/index misalignment in grouped or rolling operations, NaN/edge handling, and off-by-one issues? Penalize both code that runs but is wrong and code that would crash. If the CONTENT contains NO code at all, score 0.

== HANDLING RULES ==
- The leading JSON metadata header is harness-added, not authored. Use it only to read model_code. Never cite it as a format_violation, never count it toward the word target, and never let it affect any score. Grade only the article that follows it.
- Light formatting (subheadings, lists, occasional emphasis, inline code) is allowed and, when it aids readability, is a positive under clarity. Reserve format_violation for elements the assignment actually bans (e.g., hyperlinks, HTML, images, tables). Use poor_formatting for allowed formatting that is missing (an undifferentiated wall of text) or overused/messy — that affects clarity, not adherence.
- Evaluate code whether or not it is wrapped in a Markdown fence. Unfenced but present code is still code — do NOT score it as missing.
- "No code" means there is no program at all (no imports/function/logic), not merely a missing fence.
- If the CONTENT's prose or formula introduces a quantity, the code is expected to compute it. Code that omits things the text promised loses points on the code score and on depth.

== FLAGS ==
Attach short standardized tags for anything noteworthy (good or bad). Use only tags that clearly apply. You may append a ":detail" suffix (e.g. "missing_section:Text Formula"). Add anything else as "note: ...".

  under_length, over_length, missing_section, wrong_headings,
  format_violation, poor_formatting, no_code, code_unfenced, code_would_error,
  formula_code_mismatch, math_error, factual_error, incomplete_outputs,
  no_multientity_handling, wrong_stat_convention,
  exceptional_clarity, exceptional_depth, exceptional_code

== OUTPUT ==
Produce TWO parts, in this exact order and nothing else. Reason first, then score.

PART 1 — a section titled exactly "## Detailed Reasoning" containing one short paragraph for EVERY criterion, in the order and format shown below. Each paragraph is 1-4 sentences and must cite specific evidence from the CONTENT — name the concrete error, the missing section, the approximate word count, the exact code bug, etc. Generic justifications are not acceptable. Work out each criterion's score HERE, before writing the JSON.

## Detailed Reasoning
**Clarity (score):** ...
**Accuracy (score):** ...
**Depth (score):** ...
**Adherence (score):** ...
**Code (score):** ...
**Flags:** one line per flag you applied, each briefly justifying why it applies.

PART 2 — the scores as a single JSON object inside ONE ```json fenced code block (exactly one such block in your whole reply). Copy "model_code" verbatim from the CONTENT header. Each score MUST equal the score you assigned in the reasoning above.

```json
{"model_code":"<copy from CONTENT header>","scores":{"clarity":0,"accuracy":0,"depth":0,"adherence":0,"code":0},"flags":[],"summary":"<=30 words: the single most important strength or weakness"}
```

Output nothing after the JSON block.

================================================================================
ASSIGNMENT
----------
{content_prompt}

================================================================================
CONTENT
--------
{content_text}

================================================================================
Grade the CONTENT against the ASSIGNMENT using the rubric above. Write the Detailed Reasoning section first, then the JSON block.
"""