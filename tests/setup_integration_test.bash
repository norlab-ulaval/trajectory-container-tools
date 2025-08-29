#!/bin/bash
# ================================================================================================
# Setup integration test
#
# Usage:
#   $ bash setup_integration_test.bash
#
# Global:
#   read TEAMCITY_VERSION
#   read GITHUB_TOKEN
#   read N2ST_PATH
#
# =================================================================================================

function tnp::install_gh_cli_on_ci() {
  # Official doc: https://github.com/cli/cli/blob/trunk/docs/install_linux.md

  if [[ ${TEAMCITY_VERSION} ]] && ! command -v gh &> /dev/null; then
    echo "Test is run on a TeamCity server, install GitHub cli"
    {
      (type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
        && sudo mkdir -p -m 755 /etc/apt/keyrings \
        && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
        && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
        && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
        && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
        && sudo apt update \
        && sudo apt install gh -y ;
    } || { n2st::print_msg_error "Failed to install GitHub cli!" ; return 1 ; }
  fi

  if [[ ${TEAMCITY_VERSION} ]] && [[ -z ${GITHUB_TOKEN} ]]; then
    n2st::print_msg_error_and_exit "CI execution require that GITHUB_TOKEN be set to enable automatic GitHub cli authentification login"
  elif [[ ${TEAMCITY_VERSION} ]] && [[ -n ${GITHUB_TOKEN} ]]; then
    n2st::print_msg "GitHub cli login › Authenticating with GitHub token..."
    echo "$GITHUB_TOKEN" | gh auth login --with-token
    gh auth status # Verify authentication
  fi
  return 0
}

function tnp::install_other_requirement_on_ci() {
  if [[ ${TEAMCITY_VERSION} ]] && ! command -v jq &> /dev/null; then
    echo "Test is run on a TeamCity server,"
    sudo apt update
    echo "install JSON processor (jq) command-line"
    {
      sudo apt install --yes jq ;
    } || { n2st::print_msg_error "Failed to install JSON processor (jq)!" ; return 1 ; }
    echo "install JSON processor (jq) command-line"
    {
      sudo apt install --yes tree ;
    } || { n2st::print_msg_error "Failed to install tree!" ; return 1 ; }
  fi
  return 0
}

function tnp::setup_mock_semantic_release_files() {
  local tnp_mock_repo_path="${TNP_PATH:?err}/utilities/tmp/dockerized-norlab-project-mock-EMPTY"
  test -d "${tnp_mock_repo_path}" || n2st::print_msg_error_and_exit "The directory ${tnp_mock_repo_path} is unreachable"
  # Create a mock semantic_release.yml file
  mkdir -p "${tnp_mock_repo_path}/.github/workflows" || return 1
  {
    cat > "${tnp_mock_repo_path}/.github/workflows/semantic_release.yml" << 'EOF'
name: Semantic-release

on:
  push:
    branches:
      - main
      - beta
      - alpha
EOF

    # Create a mock .releaserc.json file
    cat > "${tnp_mock_repo_path}/.releaserc.json" << 'EOF'
{
  "branches": ["main",
    {
      "name": "beta",
      "prerelease": true
    },
    {
      "name": "alpha",
      "prerelease": true
    }
  ]
}
EOF
  } || { n2st::print_msg_error "Failed to create semantic-versionaing related files!" ; return 1 ; }
  return 0
}

# ::::Main:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  # This script is being run, ie: __name__="__main__"

  source "${N2ST_PATH:?'Variable not set'}/import_norlab_shell_script_tools_lib.bash" || exit 1

  n2st::print_formated_script_header "setup_integration_test.bash" "${MSG_LINE_CHAR_UTIL}"
  tnp::install_gh_cli_on_ci || exit 1
  tnp::install_other_requirement_on_ci || exit 1
  tnp::setup_mock_semantic_release_files || exit 1
  n2st::print_formated_script_footer "setup_integration_test.bash" "${MSG_LINE_CHAR_UTIL}"
else
  # This script is being sourced, ie: __name__="__source__"
  tnp_error_prefix="\033[1;31m[TNP error]\033[0m"
  echo -e "${tnp_error_prefix} This script must executed with bash! i.e.: $ bash $( basename "$0" )" 1>&2
  exit 1
fi
