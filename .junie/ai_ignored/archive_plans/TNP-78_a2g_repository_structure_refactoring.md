# _AI Agent Guidelines (A2G)_ repository structure refactoring plan

YouTrack task: TNP-78 refactor: Improve A2G repository structure

## Context

- _AI Agent Guidelines (A2G)_ located in `.junie/ai_agent_guidelines` is:
    - An AI agent guideline management framework;
    - A collection of guidelines for private use;
    - And is a private repository;
- The main repository `template-norlab-project` serves as a A2G deployment case study for improving
  A2G.
- Review `template-norlab-project` and A2G guidelines from an AI agent usage point of view.

## Goal

Improve A2G repository file structure organization so that it is easier to use and maintain.

## Repository structure

### Current file structure tree

```text
.junie/
├── active_plans/
├── ai_artifact/
├── ai_ignored/
├── a2g_config.yml
├── guidelines.md
└── ai_agent_guidelines/
    ├── specialized_guidelines/
    │   ├── guidelines.markdown.md
    │   ├── guidelines.n2st.md
    │   ├── guidelines.nbs.md
    │   ├── guidelines.python.md
    │   └── guidelines.shell_script.md
    ├── specialized_recipes/
    │   ├── recipes.ai_agent.md
    │   ├── recipes.general.md
    │   ├── recipes.n2st.md
    │   ├── recipes.nbs.md
    │   ├── recipes.python.md
    │   └── recipes.shell_script.md
    ├── template/
    │   └── ...
    ├── tools/
    │   └── ...
    ├── visual/
    │   └── ...
    ├── CHANGELOG.md
    ├── guidelines.a2g_framework.md
    ├── guidelines.a2g_general.md
    ├── validation_checklist.md
    ├── README.human.md
    ├── README.md
    └── version.txt
```

### Expected file structure tree

```text
.junie/
├── active_plans/
├── ai_artifact/
├── ai_ignored/
├── a2g_config.yml
├── guidelines.md
└── ai_agent_guidelines/
    ├── guidelines/
    │   ├── specialized_guidelines/
    │   │   ├── guidelines.markdown.md
    │   │   ├── guidelines.n2st.md
    │   │   ├── guidelines.nbs.md
    │   │   ├── guidelines.python.md
    │   │   └── guidelines.shell_script.md
    │   └── guidelines.a2g_general.md
    ├── recipes/
    │   ├── specialized_recipes/
    │   │   ├── recipes.ai_agent.md
    │   │   ├── recipes.n2st.md
    │   │   ├── recipes.nbs.md
    │   │   ├── recipes.python.md
    │   │   └── recipes.shell_script.md
    │   └── recipes.general.md
    ├── framework/
    │   ├── guidelines.a2g_framework.md 
    │   └── guidelines.a2g_validation_checklist.md         <- renamed from 'validation_checklist.md' 
    ├── template/
    │   └── ...
    ├── tools/
    │   └── ...
    ├── visual/
    │   └── ...
    ├── CHANGELOG.md
    ├── README.human.md
    ├── README.md
    └── version.txt
```

## Instructions

### Planning phase

1. Inspect and validate the expected file structure tree.
2. Define the **expected outcome** e.g., "A2G framework ready for optimal AI agent deployment with
   95%+ efficiency rating."
3. Provide your assessment in the console and wait for my approval before proceeding with the
   refactoring phase.

### Refactoring phase

#### Refactoring Instructions

1. Refactor directory structure according to the expected file structure tree
2. Rename files according to the expected file structure tree
3. Update A2G `.junie/ai_agent_guidelines` files references accordingly
4. Update A2G-super-project `.junie` files references accordingly
5. List files that are ai ignore but should be updated in summary

#### Refactoring Execution

Establish feedback loop for measuring AI agent guideline efficiency improvement:

1. execute refactoring phase;
2. read files and measure efficiency;
3. repeat step 1 until **expected outcome** reached (as stated above). 
