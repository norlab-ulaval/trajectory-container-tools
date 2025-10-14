# Prompt Instruction Recipes

Is AI ignore

## General

```markdown
Read and implement the plan at `.junie/active_plans/TODO.md`.
```

```markdown
# Tasks
1. Analyze codebase thoroughly to understand what it is about.
2. TODO

# Instructions
- Always comply with `.junie/guidelines.md` guidelines.
- Execute all tests before submitting.
```

## Update documentation

```markdown
# Tasks
1. Analyze codebase thoroughly to understand what it is about. 
2. Considering the changes introduced in the last 5 commits, update if relevant the `README.md`, documentations in `documentation/` directory and usage example Jupyter notebook in `notebooks/` directory.
3. Review all documentations, readme and jupyter notebook: 
   - Review the `README.md` updated version and make sure it aligns with the codebase   
   - Review the newly created documentation and make sure it aligns with the codebase.   
   - Review the jupyter notebook or make sure it align with the codebase.
   - If not, repeat from **Task step 2** and keep repeating until all condition are met.

```
