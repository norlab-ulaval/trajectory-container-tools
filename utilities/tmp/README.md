# Note on the `utilities/tmp` directory

- content of `utilities/tmp` are meant to be modified/deleted at runtime
- `tmp/dockerized-norlab-project-mock-EMPTY` is a placeholder directory (might be excluded in IDE). 
  It is needed to implement github branch protection rule logic.  
  For that reason, it is cloned as a full repository at runtime, not a submodule.  
  - In TNP, cloning and removing is manage by `setup_mock.bash` and `teardown_mock.bash` in `tests` dir.

