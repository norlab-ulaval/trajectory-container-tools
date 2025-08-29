#!/bin/bash
# ===============================================================================================
# Teardown integration test
#
# Usage:
#   $ bash teardown_integration_test.bash
#
# Requirement: Must be executed before 'tnp::teardown_mock' function
#
# Notes:
#   See utilities/tmp/README.md for details on role of `dockerized-norlab-project-mock-EMPTY`
#
# Global:
#   read TNP_PATH
#   read N2ST_PATH
#
# =================================================================================================


function tnp::reset_mock_repository_github_config() {
  local non_default_branches=( "$@" )
  # Remove any branch protection rules that might have been added during testing
  # Note: This requires the repository to be accessible and the user to have admin rights

  local tnp_mock_repo_path="${TNP_PATH:?err}/utilities/tmp/dockerized-norlab-project-mock-EMPTY"

  if [[ -d "${tnp_mock_repo_path}" ]]; then
    echo "Resetting GitHub repository settings..."
    local tmp_cwd
    tmp_cwd=$(pwd)

    cd "${tnp_mock_repo_path}" || return 1

    # ....Begin....................................................................................
    if command -v gh &> /dev/null && gh auth status &> /dev/null 2>&1; then
      echo "Removing test branch protection rules..."

      # Reverting repo release branch to original state
      if ! git show-ref --verify --quiet "refs/heads/main" || \
        ! git show-ref --verify --quiet "refs/remotes/origin/main"; then
          git branch -m "main"
          git push -u origin "main"
          gh repo edit --default-branch "main"
      fi

      # Get repository info
      local repo_info
      local repo_owner
      local repo_name
      repo_info=$(gh repo view --json owner,name 2>/dev/null || echo '{"owner":{"login":""},"name":""}')
      repo_owner=$(echo "$repo_info" | jq -r '.owner.login')
      repo_name=$(echo "$repo_info" | jq -r '.name')

      if [[ -n "$repo_owner" && -n "$repo_name" && "$repo_owner" != "null" && "$repo_name" != "null" ]]; then
        # Remove protection from main and dev branches if they exist
        local branches_name=("main" "dev" "beta" "${non_default_branches[@]}" )
        for each_branch in "${branches_name[@]}"; do
          echo "Check branch: ${each_branch}"
          if git show-ref --verify --quiet "refs/remotes/origin/${each_branch}" 2>/dev/null; then
            echo "Removing protection from branch: ${each_branch}"
            gh api --silent --method DELETE "/repos/$repo_owner/$repo_name/branches/${each_branch}/protection" 2>/dev/null || echo "No protection to remove for ${each_branch}"
          else
            echo "No branch ${each_branch}"
          fi
        done

        # Delete branches local and remote except default branch
        local branches_name=("dev" "beta" "${non_default_branches[@]}" )
        for each_branch in "${branches_name[@]}"; do
          if git show-ref --verify --quiet "refs/heads/${each_branch}"; then
            # Delete local branch if it exist
            git branch -d "${each_branch}"
          fi
          if git show-ref --verify --quiet "refs/remotes/origin/${each_branch}"; then
            # Delete remote branch if it exist
            git push origin --delete "${each_branch}"
          fi
        done
      fi
    fi

  fi
  # ....Teardown...................................................................................
  cd "${tmp_cwd}" || return 1
  return 0
}


function tnp::teardown_mock_semantic_release_files() {
  local tnp_mock_repo_path="${TNP_PATH:?err}/utilities/tmp/dockerized-norlab-project-mock-EMPTY"
  {
    rm -R "${tnp_mock_repo_path}/.github/workflows" && \
    rm -R "${tnp_mock_repo_path}/.releaserc.json" ;
  } || tree -L 2 -a "${tnp_mock_repo_path}"

  n2st::print_formated_script_footer "teardown_integration_test.bash" "${MSG_LINE_CHAR_UTIL}"
  return 0
}


# ::::Main:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  # This script is being run, ie: __name__="__main__"

  source "${N2ST_PATH:?'Variable not set'}/import_norlab_shell_script_tools_lib.bash" || exit 1

  n2st::print_formated_script_header "teardown_integration_test.bash" "${MSG_LINE_CHAR_UTIL}"
  tnp::reset_mock_repository_github_config "$@"
  tnp::teardown_mock_semantic_release_files
  n2st::print_formated_script_footer "teardown_integration_test.bash" "${MSG_LINE_CHAR_UTIL}"
else
  # This script is being sourced, ie: __name__="__source__"
  tnp_error_prefix="\033[1;31m[TNP error]\033[0m"
  echo -e "${tnp_error_prefix} This script must executed with bash! i.e.: $ bash $( basename "$0" )" 1>&2
  exit 1
fi


