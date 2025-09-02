# Repository Guidelines

_Trajectory Container Tools (TCT)_ guidelines and instructions

## Repository Description

A library for managing trajectory related data. Provide trajectory dataclasses of various type, factory function, rosbag extractor, pandas dataframe extractor and various utilities.

## Repository Guidelines Instructions

1. First, review and learn _A2G Framework Guidelines_ specified in
  `.junie/ai_agent_guidelines/guidelines.a2g_framework.md`.
2. Then review the remaining repository guidelines below.

## Prime directive:

Always comply with _A2G Framework Guidelines_, _Repository Guidelines_ and _AI operator_ instructions.

## Repository Organization

- `.dockerized_norlab` contains DNA configuration files.
- `.junie/` contains AI agent related files.
- `.junie/ai_agent_guidelines` contains _AI Agent Guidelines (A2G)_ with entrypoint at
  `.junie/ai_agent_guidelines/README.md`.
- `src/` contains repository source code.
- `tests/` contains tests files.
- `artifact/` contains project artifact such as experimental log, plot and rosbag.
- `utilities/` contains external libraries.

## Repository Terminology

- **TCT**: Acronym for _Trajectory Container Tools_ i.e., the current repository. 
- **DNA**: Dockerized-NorLab project application.
- **MG**: Acronym for _Math Gymnasium_.
- **RLRC**: Acronym for _RedLeader-research-codebase_.
- **R2S2R**: Real to sim to real → Real environment to simulated environment to real environment. 
- **RL**: Reinforcement-Learning → Is an AI learning base paradigme where an agent learns a policy by interacting with its environment.      
- **Deep-RL**: Deep Reinforcement-Learning → A deep-learning variant of RL.
- **Model-Based RL**: Model-based Reinforcement-Learning → RL method where the algorithm explicitly learns the environment model i.e., the system dynamic.
- **Controller**: Control Theory analogue of a policy. Usualy imply a know motion dynamic and a cost instead of a reward. Usualy the term used in robotic. 
- **Resilient controller**: Controller that can cop with adverse condition in such a way that they fall on their feet after losing control.

## Repository Specific Additional Guidelines

Proceed with _AI operator_ instructions
