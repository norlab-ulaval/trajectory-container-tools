#!/bin/bash
# =================================================================================================
# Run all tests script in tests_dryrun_and_tests_scripts
#
# Usage:
#   $ bash run_all_dryrun_and_tests_scripts.bash
#
# =================================================================================================

MSG_ERROR_FORMAT="\033[1;31m"
MSG_DONE_FORMAT="\033[1;32m"
MSG_END_FORMAT="\033[0m"

# ....Setup........................................................................................
if [[ ${TEAMCITY_VERSION} ]]; then
  # Assuming is run in a TC docker run wrapper

  export DEBIAN_FRONTEND=noninteractive
  apt-get update \
    && apt-get install --assume-yes --no-install-recommends \
        locales \
        sudo \
        lsb-release \
        curl \
        wget \
        ca-certificates \
        git \
        tree \
        zip gzip tar unzip \
        fontconfig \
        software-properties-common \
    && rm -rf /var/lib/apt/lists/*

  locale-gen en_US en_US.UTF-8 && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

  # This is required in our case since we deal with git submodule
  git config --global --add safe.directory "*"

  git config --global credential.helper store
  git config --global user.name "RedLeader962"
  git config --global user.email "redleader962@gmail.com"
  git config --global url.https://"${GITHUB_TOKEN}"@github.com/.insteadOf https://github.com/

  unset DEBIAN_FRONTEND
fi

# ....Begin........................................................................................
tnp_root=$(git rev-parse --show-toplevel)

bash "${tnp_root}/tests/tests_dryrun_and_tests_scripts/dryrun_configure_github_branch_protection.bash"
EXIT_CODE1=$?

if [[ ${EXIT_CODE1} == 0 ]]; then
  bash "${tnp_root}/tests/tests_dryrun_and_tests_scripts/test_configure_github_branch_protection.bash"
  EXIT_CODE2=$?
else
  echo -e "${MSG_ERROR_FORMAT}Dry-run failure! Skip test_configure_github_branch_protection.bash execution${MSG_END_FORMAT}\n"
  EXIT_CODE2=1
fi

# ....Teardown.....................................................................................

echo -e "Completed execution of:
  - dryrun_configure_github_branch_protection.bash
  - test_configure_github_branch_protection.bash
"

all_exit_code=$((EXIT_CODE1 + EXIT_CODE2))
if [[ ${all_exit_code} == 0 ]]; then
  echo -e "${MSG_DONE_FORMAT}[TNP done] ✓ All integration tests completed successfully!${MSG_END_FORMAT}"
else
  echo -e "${MSG_ERROR_FORMAT}[TNP error] ✗ Integration tests completed with failure!${MSG_END_FORMAT}"
fi

exit ${all_exit_code}
