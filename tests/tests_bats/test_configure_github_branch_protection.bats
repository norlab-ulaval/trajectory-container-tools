#!/usr/bin/env bats
#
# Usage in docker container
#   $ REPO_ROOT=$(pwd) && RUN_TESTS_IN_DIR='tests'
#   $ docker run -it --rm -v "$REPO_ROOT:/code" bats/bats:latest "$RUN_TESTS_IN_DIR"
#
#   Note: "/code" is the working directory in the bats official image
#
# bats-core ref:
#   - https://bats-core.readthedocs.io/en/stable/tutorial.html
#   - https://bats-core.readthedocs.io/en/stable/writing-tests.html
#   - https://opensource.com/article/19/2/testing-bash-bats
#       ↳ https://github.com/dmlond/how_to_bats/blob/master/test/build.bats
#
# Helper library: 
#   - https://github.com/bats-core/bats-assert
#   - https://github.com/bats-core/bats-support
#   - https://github.com/bats-core/bats-file
#

BATS_HELPER_PATH=/usr/lib/bats
if [[ -d ${BATS_HELPER_PATH} ]]; then
  load "${BATS_HELPER_PATH}/bats-support/load"
  load "${BATS_HELPER_PATH}/bats-assert/load"
  load "${BATS_HELPER_PATH}/bats-file/load"
  load "${SRC_CODE_PATH}/${N2ST_BATS_TESTING_TOOLS_RELATIVE_PATH}/bats_helper_functions"
  load "${SRC_CODE_PATH}/tests/tests_bats/bats_testing_tools/bats_helper_functions_local"
  #load "${BATS_HELPER_PATH}/bats-detik/load" # << Kubernetes support
else
  echo -e "\n[\033[1;31mERROR\033[0m] $0 path to bats-core helper library unreachable at \"${BATS_HELPER_PATH}\"!" 1>&2
  echo '(press any key to exit)'
  read -r -n 1
  exit 1
fi

# ====Setup========================================================================================

TESTED_FILE="configure_github_branch_protection.bash"

# executed once before starting the first test (valide for all test in that file)
setup_file() {
  BATS_DOCKER_WORKDIR=$(pwd) && export BATS_DOCKER_WORKDIR

  export TNP_MOCK_REPO_PATH="${BATS_DOCKER_WORKDIR}/utilities/tmp/dockerized-norlab-project-mock-EMPTY"
  export N2ST_PATH="${BATS_DOCKER_WORKDIR}/utilities/norlab-shell-script-tools"

  ## Uncomment the following for debug, the ">&3" is for printing bats msg to stdin
  #tree -L 1 -a -hug "${PWD}" >&3

  apt-get update && \
      apt-get install --yes jq
}

# executed before each test
setup() {
  source "${BATS_DOCKER_WORKDIR}/${TESTED_FILE}"

  cd "${TNP_MOCK_REPO_PATH}" || exit 1

  # Create a mock semantic_release.yml file
  mkdir -p .github/workflows
  cat > .github/workflows/semantic_release.yml << 'EOF'
name: Semantic-release

on:
  push:
    branches:
      - main
      - beta
      - alpha
EOF

  # Create a mock .releaserc.json file
  cat > .releaserc.json << 'EOF'
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

}

# ====Teardown=====================================================================================

# executed after each test
teardown() {
  rm -R "${TNP_MOCK_REPO_PATH}/.github/workflows/semantic_release.yml"
  rm -R "${TNP_MOCK_REPO_PATH}/.releaserc.json"
  cd "${BATS_DOCKER_WORKDIR}" || exit 1
}

# ====Tests========================================================================================

@test "gbp::validate_prerequisites should fail when gh is not installed" {

  run gbp::validate_prerequisites
  assert_failure
  assert_output --partial "GitHub CLI (gh) is not installed"
}

@test "gbp::validate_prerequisites should fail when not authenticated" {
  # Mock gh command to simulate not authenticated
  function gh() {
    if [[ "$1" == "auth" && "$2" == "status" ]]; then
      return 1
    fi
  }
  export -f gh

  run gbp::validate_prerequisites
  assert_failure
  assert_output --partial "GitHub CLI is not authenticated"
}

@test "gbp::validate_prerequisites should fail when not in git repository" {
  # Mock gh command
  function gh() {
    return 0
  }
  export -f gh

  # Mock git command to simulate not in git repository
  function git() {
    if [[ "$1" == "rev-parse" ]]; then
      return 1
    fi
  }
  export -f git

  run gbp::validate_prerequisites
  assert_failure
  assert_output --partial "Current directory is not a git repository"
}

@test "gbp::validate_prerequisites should fail when not GitHub repository" {
  # Mock git command to simulate non-GitHub repository
  function git() {
    if [[ "$1" == "rev-parse" ]]; then
      return 0
    elif [[ "$1" == "config" ]]; then
      echo "https://gitlab.com/user/repo.git"
    fi
  }
  export -f git

  # Mock gh command to simulate installed and authenticated
  function gh() {
    if [[ "$1" == "auth" && "$2" == "status" ]]; then
      return 0
    fi
  }
  export -f gh

  run gbp::validate_prerequisites
  assert_failure
  assert_output --partial "Repository is not hosted on GitHub"
}

@test "gbp::get_repository_info should extract owner, name and default branch correctly" {
  # Mock gh repo view command
  function gh() {
    if [[ "$1" == "repo" && "$2" == "view" ]]; then
      echo '{"owner":{"login":"norlab-ulaval"},"name":"test-repo","defaultBranchRef":{"name":"main"}}'
    fi
  }
  export -f gh

  run gbp::get_repository_info
  assert_success
  assert_output --partial "Repository: norlab-ulaval/test-repo (default branch: main)"
}

@test "gbp::create_branch_if_not_exists should work in dry-run mode" {
  run gbp::create_branch_if_not_exists "test-branch" "true"
  assert_success
  assert_output --partial "DRY RUN: Would create branch 'test-branch'"
}

@test "gbp::create_branch_if_not_exists should skip if branch exists" {
  # Mock git show-ref to simulate existing branch
  function git() {
    if [[ "$1" == "show-ref" ]]; then
      return 0  # Branch exists
    fi
  }
  export -f git

  run gbp::create_branch_if_not_exists "existing-branch" "false"
  assert_success
  assert_output --partial "Branch 'existing-branch' already exists"
}

@test "gbp::rename_branch_if_needed should skip when using default branch name" {
  REPO_DEFAULT_BRANCH="main"
  export REPO_DEFAULT_BRANCH

  run gbp::rename_branch_if_needed "main" "false"
  assert_success
  # Should return 0 without any output since it's using default name
}

@test "gbp::rename_branch_if_needed should work in dry-run mode" {
  REPO_DEFAULT_BRANCH="main"
  export REPO_DEFAULT_BRANCH

  # Mock git show-ref to simulate main exists, target doesn't exist
  function git() {
    if [[ "$1" == "show-ref" && "$4" == "refs/heads/main" ]]; then
      return 0  # main branch exists
    elif [[ "$1" == "show-ref" && "$4" == "refs/remotes/origin/main" ]]; then
      return 0  # main branch exists on remote
    elif [[ "$1" == "show-ref" && "$4" == "refs/heads/master" ]]; then
      return 1  # master branch doesn't exist
    elif [[ "$1" == "show-ref" && "$4" == "refs/remotes/origin/master" ]]; then
      return 1  # master branch doesn't exist on remote
    fi
  }
  export -f git

  run gbp::rename_branch_if_needed "master" "true"
  assert_success
  assert_output --partial "DRY RUN: Would rename branch 'main' to 'master'"
}

@test "gbp::rename_branch_if_needed should skip when default branch doesn't exist" {
  REPO_DEFAULT_BRANCH="main"
  export REPO_DEFAULT_BRANCH

  # Mock git show-ref to simulate main doesn't exist
  function git() {
    if [[ "$1" == "show-ref" ]]; then
      return 1  # No branches exist
    fi
  }
  export -f git

  run gbp::rename_branch_if_needed "master" "false"
  assert_success
  # Should return 0 without renaming since main doesn't exist
}

@test "gbp::rename_branch_if_needed should skip when target branch already exists" {
  REPO_DEFAULT_BRANCH="main"
  export REPO_DEFAULT_BRANCH

  # Mock git show-ref to simulate both branches exist
  function git() {
    if [[ "$1" == "show-ref" ]]; then
      return 0  # Both branches exist
    fi
  }
  export -f git

  run gbp::rename_branch_if_needed "master" "false"
  assert_success
  # Should return 0 without renaming since target already exists
}

@test "gbp::configure_branch_protection should work in dry-run mode" {
  # Mock repository info
  REPO_OWNER="norlab-ulaval"
  REPO_NAME="test-repo"

  run gbp::configure_branch_protection "main" "true"
  assert_success
  assert_output --partial "DRY RUN: Would configure main with:"
  assert_output --partial "required_pull_request_reviews"
}

@test "gbp::configure_branch_protection should call GitHub API correctly" {
  # Mock repository info
  REPO_OWNER="norlab-ulaval"
  REPO_NAME="test-repo"

  # Mock gh api command
  function gh() {
    if [[ "$1" == "api" ]]; then
      # Verify correct API endpoint is called
      assert_equal "$4" "/repos/norlab-ulaval/test-repo/branches/main/protection"
      return 0
    fi
  }
  export -f gh

  run gbp::configure_branch_protection "main" "false"
  assert_success
  assert_output --partial "Branch protection configured for: main"
}

@test "gbp::configure_repository_settings should work in dry-run mode" {
  run gbp::configure_repository_settings "true"
  assert_success
  assert_output --partial "DRY RUN: Would configure repository with:"
  assert_output --partial "gh repo edit"
  assert_output --partial "--enable-auto-merge"
  assert_output --partial "--delete-branch-on-merge"
  assert_output --partial "--enable-merge-commit"
  assert_output --partial "--enable-squash-merge"
  assert_output --partial "--allow-update-branch"
}

@test "gbp::configure_repository_settings should call gh repo edit correctly" {
  # Mock gh repo edit command
  function gh() {
    if [[ "$1" == "repo" && "$2" == "edit" ]]; then
      # Verify correct flags are passed
      local expected_flags=(
        "--enable-auto-merge"
        "--delete-branch-on-merge"
        "--enable-merge-commit"
        "--enable-squash-merge"
        "--allow-update-branch"
      )

      for flag in "${expected_flags[@]}"; do
        if [[ ! " $* " =~ " $flag " ]]; then
          echo "Missing flag: $flag"
          return 1
        fi
      done
      return 0
    fi
  }
  export -f gh

  run gbp::configure_repository_settings "false"
  assert_success
  assert_output --partial "Repository-wide settings configured"
}

@test "gbp::configure_repository_settings should handle gh repo edit failure" {
  # Mock gh repo edit command to fail
  function gh() {
    if [[ "$1" == "repo" && "$2" == "edit" ]]; then
      return 1
    fi
  }
  export -f gh

  run gbp::configure_repository_settings "false"
  assert_failure
  assert_output --partial "Failed to configure repository-wide settings"
}


@test "gbp::show_help should display correct usage information" {
  run gbp::show_help
  assert_success
  assert_output --partial "Configure GitHub branch protection rules"
  assert_output --partial "--dry-run"
  assert_output --partial "--release-branch"
  assert_output --partial "--dev-branch"
}

@test "gbp::main should handle configurable branch names" {
  # Mock all required functions
  function gbp::validate_prerequisites() { return 0; }
  function gbp::get_repository_info() { 
    REPO_OWNER="test-owner"
    REPO_NAME="test-repo"
    REPO_DEFAULT_BRANCH="main"
  }
  function gbp::configure_repository_settings() { return 0; }
  function gbp::create_branch_if_not_exists() { return 0; }
  function gbp::configure_branch_protection() { return 0; }
  function n2st::norlab_splash() { return 0; }
  function n2st::print_formated_script_header() { return 0; }
  function n2st::print_msg_done() { return 0; }
  function n2st::print_formated_script_footer() { return 0; }
  function n2st::print_msg() { return 0; }
  export -f gbp::validate_prerequisites gbp::get_repository_info gbp::configure_repository_settings
  export -f gbp::create_branch_if_not_exists gbp::configure_branch_protection
  export -f n2st::norlab_splash n2st::print_formated_script_header n2st::print_msg_done n2st::print_formated_script_footer n2st::print_msg

  run gbp::main --dry-run --release-branch "master" --dev-branch "develop"
  assert_success
}

@test "gbp::main should handle help option" {
  run gbp::main --help
  assert_success
  assert_output --partial "Configure GitHub branch protection rules"
}

@test "gbp::main should handle invalid arguments" {
  # Mock n2st functions to avoid errors
  function n2st::print_msg_error() { echo "Error: $*"; }
  export -f n2st::print_msg_error

  run gbp::main --invalid-option
  assert_failure
  assert_output --partial "Unknown option: --invalid-option"
}

@test "gbp::main should handle single branch configuration" {
  # Mock all required functions
  function gbp::validate_prerequisites() { return 0; }
  function gbp::get_repository_info() { 
    REPO_OWNER="test-owner"
    REPO_NAME="test-repo"
    REPO_DEFAULT_BRANCH="main"
  }
  function gbp::configure_repository_settings() { return 0; }
  function gbp::update_releaserc_json() { return 0; }
  function gbp::update_semantic_release_yml() { return 0; }
  function gbp::create_branch_if_not_exists() { return 0; }
  function gbp::configure_branch_protection() { return 0; }
  function n2st::norlab_splash() { return 0; }
  function n2st::print_formated_script_header() { return 0; }
  function n2st::print_msg_done() { return 0; }
  function n2st::print_formated_script_footer() { return 0; }
  function n2st::print_msg() { return 0; }
  export -f gbp::validate_prerequisites gbp::get_repository_info gbp::configure_repository_settings
  export -f gbp::update_releaserc_json gbp::update_semantic_release_yml gbp::create_branch_if_not_exists gbp::configure_branch_protection
  export -f n2st::norlab_splash n2st::print_formated_script_header n2st::print_msg_done n2st::print_formated_script_footer n2st::print_msg

  run gbp::main --dry-run --branch "main"
  assert_success
}

@test "gbp::update_releaserc_json should work in dry-run mode" {
  run gbp::update_releaserc_json "master" "true"
  assert_success
  assert_output --partial "DRY RUN: Would update .releaserc.json:"
  assert_output --partial "Release branch: master"
}

@test "gbp::update_releaserc_json should skip when using default branch name" {
  REPO_DEFAULT_BRANCH="main"
  export REPO_DEFAULT_BRANCH

  run gbp::update_releaserc_json "main" "false"
  assert_success
  assert_output --partial "Using default release branch name, no .releaserc.json update needed"
}

@test "gbp::update_releaserc_json should handle missing .releaserc.json file" {
  # Ensure no .releaserc.json file exists
  rm -f .releaserc.json

  run gbp::update_releaserc_json "master" "false"
  assert_success
  assert_output --partial ".releaserc.json not found, skipping semantic-release configuration update"
}

@test "gbp::update_releaserc_json should update file with custom branch name" {
  # Mock jq to return success
  function jq() {
    echo '{"branches":["master",{"name":"beta","prerelease":true},{"name":"alpha","prerelease":true}]}'
    return 0
  }
  export -f jq

  run gbp::update_releaserc_json "master" "false"
  assert_success
  assert_output --partial ".releaserc.json updated successfully"
  assert_output --partial "Backup saved as .releaserc.json.backup"
}

@test "gbp::update_semantic_release_yml should work in dry-run mode" {

  run gbp::update_semantic_release_yml "master" "true"
  assert_success
  assert_output --partial "DRY RUN: Would update .github/workflows/semantic_release.yml:"
  assert_output --partial "Release branch: master"
}

@test "gbp::update_semantic_release_yml should skip when using default branch name" {
  REPO_DEFAULT_BRANCH="main"
  export REPO_DEFAULT_BRANCH

  run gbp::update_semantic_release_yml "main" "false"
  assert_success
  assert_output --partial "Using default release branch name, no semantic_release.yml update needed"
}

@test "gbp::update_semantic_release_yml should handle missing semantic_release.yml file" {
  # Ensure no semantic_release.yml file exists
  rm -rf .github

  run gbp::update_semantic_release_yml "master" "false"
  assert_success
  assert_output --partial ".github/workflows/semantic_release.yml not found, skipping workflow update"
}

@test "gbp::update_semantic_release_yml should update file with custom branch name" {

  # Mock sed to return success
  function sed() {
    if [[ "$1" == "-i.tmp" ]]; then
      echo "mocked sed success"
      return 0
    fi
  }
  export -f sed

  run gbp::update_semantic_release_yml "master" "false"
  assert_success
  assert_output --partial "semantic_release.yml updated successfully"
  assert_output --partial "Backup saved as .github/workflows/semantic_release.yml.backup"
}


@test "gbp::main should configure both branches by default" {
  # Mock all required functions
  function gbp::validate_prerequisites() { return 0; }
  function gbp::get_repository_info() { 
    REPO_OWNER="test-owner"
    REPO_NAME="test-repo"
    REPO_DEFAULT_BRANCH="main"
  }
  function gbp::update_releaserc_json() { return 0; }
  function gbp::update_semantic_release_yml() { return 0; }
  function gbp::create_branch_if_not_exists() { 
    echo "Processing branch: $1"
    return 0
  }
  function gbp::configure_branch_protection() { return 0; }
  function n2st::norlab_splash() { return 0; }
  function n2st::print_formated_script_header() { return 0; }
  function n2st::print_msg_done() { return 0; }
  function n2st::print_formated_script_footer() { return 0; }
  function n2st::print_msg() { 
    echo "$*"
    return 0
  }
  export -f gbp::validate_prerequisites gbp::get_repository_info
  export -f gbp::update_releaserc_json gbp::update_semantic_release_yml gbp::create_branch_if_not_exists gbp::configure_branch_protection
  export -f n2st::norlab_splash n2st::print_formated_script_header n2st::print_msg_done n2st::print_formated_script_footer n2st::print_msg

  run gbp::main --dry-run
  assert_success
  assert_output --partial "Processing branch: main"
  assert_output --partial "Processing branch: beta"
  assert_output --partial "Processing branch: dev"
}

# ====Standalone Mode Tests=======================================================================

@test "standalone mode should work when N2ST_PATH is not set" {
  # Unset N2ST_PATH to simulate standalone mode
  unset N2ST_PATH

  # Mock git commands for standalone mode
  function git() {
    case "$1" in
      "rev-parse")
        if [[ "$2" == "--show-toplevel" ]]; then
          echo "${TNP_MOCK_REPO_PATH}"
        fi
        ;;
      "submodule")
        echo "Mock: git submodule add norlab-shell-script-tools"
        return 0
        ;;
      "add"|"commit")
        echo "Mock: git $*"
        return 0
        ;;
      *)
        return 0
        ;;
    esac
  }
  export -f git

  # Mock directory check to simulate submodule doesn't exist
  function test() {
    if [[ "$1" == "-d" && "$2" == "${TNP_MOCK_REPO_PATH}/utilities/norlab-shell-script-tools" ]]; then
      return 1  # Directory doesn't exist
    fi
    return 0
  }
  export -f test

  # Create the submodule directory structure to simulate successful cloning
  mkdir -p "${TNP_MOCK_REPO_PATH}/utilities/norlab-shell-script-tools"

  # Test the actual script execution in standalone mode
  run bash "${BATS_DOCKER_WORKDIR}/${TESTED_FILE}" --help
  assert_output --partial "[TNP] The N2ST_PATH env var is not set! Assuming we are in stand alone mode"

  # Clean up
  rm -rf "${TNP_MOCK_REPO_PATH}/utilities/norlab-shell-script-tools"
}

@test "standalone mode should skip cloning when submodule already exists" {
  # Unset N2ST_PATH to simulate standalone mode
  unset N2ST_PATH

  # Mock git commands
  function git() {
    if [[ "$1" == "rev-parse" && "$2" == "--show-toplevel" ]]; then
      echo "${TNP_MOCK_REPO_PATH}"
    fi
    return 0
  }
  export -f git

  # Create the submodule directory to simulate it already exists
  mkdir -p "${TNP_MOCK_REPO_PATH}/utilities/norlab-shell-script-tools"

  # Create a minimal import file to avoid errors
  cat > "${TNP_MOCK_REPO_PATH}/utilities/norlab-shell-script-tools/import_norlab_shell_script_tools_lib.bash" << EOF
echo "Mock N2ST import"

function n2st::draw_horizontal_line_across_the_terminal_window() {
  return 0
}
export -f  n2st::draw_horizontal_line_across_the_terminal_window
EOF

  # Test the actual script execution when submodule exists
  run bash "${BATS_DOCKER_WORKDIR}/${TESTED_FILE}" --help
  assert_output --partial "[TNP] The N2ST_PATH env var is not set! Assuming we are in stand alone mode"
  refute_output --partial "norlab-shell-script-tools is unreachable, cloning now"

  # Clean up
  rm -rf "${TNP_MOCK_REPO_PATH}/utilities/norlab-shell-script-tools"
}

@test "standalone mode should work when N2ST_PATH is already set" {
  # Set N2ST_PATH to simulate it's already configured
  export N2ST_PATH="${BATS_DOCKER_WORKDIR}/utilities/norlab-shell-script-tools"

  # Test the actual script execution when N2ST_PATH is set
  run bash "${BATS_DOCKER_WORKDIR}/${TESTED_FILE}" --help
  assert_success
  refute_output --partial "Assuming we are in stand alone mode"
}
