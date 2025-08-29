# Description

TODO: Add a quick summary here.  


# Commit Checklist:

## Code related
- [ ] My commit messages follow the [conventional commits](https://www.conventionalcommits.org) specification. See `commit_msg_reference.md` in the repository root for details
- [ ] All tests pass locally with my changes (Check `tests/README.md` for local testing procedure) 
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] I have made corresponding changes to the documentation (i.e.: function/class, script header, README.md)
- [ ] I have commented hard-to-understand code 

## PR creation related 
- [ ] My pull request `base ref` branch is set to the `dev` branch (the _build-system_ won't be triggered otherwise) 
- [ ] My pull request branch is up-to-date with the `dev` branch (the _build-system_ will reject it otherwise)

# Note for repository admins
- Only repository admins have the privilege to `push/merge` on release, pre-release and bleeding edge branches (ie: `main`, `beta` and `dev`).
- On merge to a release or pre-release branch, it triggers the _semantic-release automation_
