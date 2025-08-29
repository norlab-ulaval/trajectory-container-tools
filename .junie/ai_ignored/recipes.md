# Prompt Instruction Recipes

Is AI ignore

## General

```markdown
Evaluate A2G performance from an AI agent usage point of view using `template-norlab-project` as a A2g-consumer-project.
```

```markdown
Read and implement the plan at `.junie/active_plans/TODO.md`.
```

```markdown
I have made minor modification to the plan at `.junie/active_plans/TODO`
Establish feedback loop for measuring AI agent guideline efficiency improvement:
1. implementation plan;
2. read files and measure efficiency;
3. repeat step 1 until **expected outcome** reached (as stated in the plan).
```

```markdown
Review guidelines at `.junie/guidelines.md`.
Execute all unit-tests and all integration tests before submitting.
```

```markdown
Add/refactor/improve `FILE_NAME`
Check if it introduce any breaking change in the code base by running both unit-tests and integration tests.
Propose source code change if relevant.
Update Markdown documentation accordingly. 
```

```markdown
Inspire yourself with ....
```

```markdown
### Implementation Strategy

Definition: **expected outcome** -> "A2G framework ready for optimal AI agent deployment with 95%+ efficiency rating."

Establish feedback loop for measuring AI agent guideline efficiency improvement:
1. execute implementation phase;
2. read files and measure efficiency;
3. repeat step 1 until **expected outcome** reached (as stated above).
```

## A2G-consumer-project pov

### A2G-consumer-project pov › Assess And Improve A2G

```markdown
# Context

- _AI Agent Guidelines (A2G)_ located in `.junie/ai_agent_guidelines` is:
    - An AI agent guideline management framework;
    - A collection of guidelines for private use;
    - And is a private repository;
- The main repository `template-norlab-project` serves as a A2G deployment case study for improving
  A2G.
- Review `template-norlab-project` and A2G guidelines from an AI agent usage point of view. 

# Goal

The goal is to assess and improve A2G and A2G-consumer-project integration.

# Task 1

Review A2G-consumer-project guidelines from an AI agent point of view:

- Assess instruction clarity;
- Highlight ambiguous or contradicting instructions;
- Does it need improvement before being used efficiently by Junie?

# Task 2

Base on task 1 report, propose an improvement plan writen to a distinct document.

# General instruction

- Make the report intuitive e.g., use emoji ✅ ❌;
- When task 1 is done, start task 2 right away.
```

### A2G-consumer-project pov › Single Tasks

```markdown
# Context

- _AI Agent Guidelines (A2G)_ located in `.junie/ai_agent_guidelines` is:
    - An AI agent guideline management framework;
    - A collection of guidelines for private use;
    - And is a private repository;
- The main repository `template-norlab-project` serves as a A2G deployment case study for improving
  A2G.
- Review `template-norlab-project` and A2G guidelines from an AI agent usage point of view. 

# Goal

The goal is to...

# Task

TODO

```

### A2G-consumer-project pov › Sequential Tasks

```markdown
# Context

- _AI Agent Guidelines (A2G)_ located in `.junie/ai_agent_guidelines` is:
    - An AI agent guideline management framework;
    - A collection of guidelines for private use;
    - And is a private repository;
- The main repository `template-norlab-project` serves as a A2G deployment case study for improving
  A2G.
- Review `template-norlab-project` and A2G guidelines from an AI agent usage point of view. 

# Goal

The goal is to...

# Task 1

TODO

# Task 2

TODO

# General instruction

- When task 1 is done, start task 2 right away.
```

## Improve/refactor source code

```markdown
Refactor/improve `FILE_NAME`.
TODO
Review guidelines at `.junie/guidelines.md`.
Update `test_FILE_NAME` accordingly.
Create at least one test case per new command argument and/or options, update current tests cases
otherwise.
Test relevant option and arguments combination.
Check if it introduce any breaking change in the code base by running both unit-tests and
integration tests.
Propose source code change if relevant.
Update Markdown documentation accordingly.
Execute all unit-tests and all integration tests before submitting.
```

## Modify proposed tests solutions

```markdown
Integration tests `test_FILE_NAME1` and `test_FILE_NAME2` are all failing.
Please investigate and make the required changes.
Review guidelines at `.junie/guidelines.md`.
```

```markdown
You overcomplicated `FILE_NAME` new test cases.
Don't test flag that are not part of the source code definition even if they are mentioned in the doc.
You only need a test case for TODO
```

````markdown
The following proposed code in `FILE_NAME1` is overcomplicated

```shell
TODO
```

Instead, inspire yourself with `FILE_NAME2` implementation:

```shell
TODO
```

Its clearer, explicit and more intuitive.
````
 
