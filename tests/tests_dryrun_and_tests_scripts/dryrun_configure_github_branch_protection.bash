#!/bin/bash
# =================================================================================================
# Integration test for GitHub branch protection configuration
# Note: This test requires a test repository and proper GitHub authentication
# =================================================================================================

set -e


function tnp::test_prerequisites_validation() {
    echo "Testing prerequisites validation..."

    cd "${TNP_MOCK_REPO_PATH}"

    # Test with valid environment
    if bash "${TNP_PATH}"/configure_github_branch_protection.bash --help > /dev/null; then
        n2st::print_msg_done "✓ Prerequisites validation passed"
    else
        n2st::print_msg_error "✗ Prerequisites validation failed"
        return 1
    fi
}

function tnp::test_help_output() {
    echo "Testing help output..."

    cd "${TNP_MOCK_REPO_PATH}"

    local help_output
    help_output=$(bash "${TNP_PATH}"/configure_github_branch_protection.bash --help)

    if [[ "$help_output" =~ "Usage:" ]] && [[ "$help_output" =~ "--dry-run" ]]; then
        n2st::print_msg_done "✓ Help output is correct"
    else
        n2st::print_msg_error "✗ Help output is incorrect"
        return 1
    fi
}

function tnp::test_argument_parsing() {
    echo "Testing argument parsing..."

    cd "${TNP_MOCK_REPO_PATH}"

    # Test invalid argument
    if ! bash "${TNP_PATH}"/configure_github_branch_protection.bash --invalid-arg 2>/dev/null; then
        n2st::print_msg_done "✓ Invalid argument handling works"
    else
        n2st::print_msg_error "✗ Invalid argument handling failed"
        return 1
    fi
}

function tnp::test_custom_branch_names() {
    echo "Testing custom branch names argument parsing..."

    cd "${TNP_MOCK_REPO_PATH}"

    # Test custom branch names help output
    local help_output
    help_output=$(bash "${TNP_PATH}"/configure_github_branch_protection.bash --help)

    if [[ "$help_output" =~ "--release-branch" ]] && [[ "$help_output" =~ "--dev-branch" ]]; then
        n2st::print_msg_done "✓ Custom branch names arguments are documented"
    else
        n2st::print_msg_error "✗ Custom branch names arguments not found in help"
        return 1
    fi
}

function tnp::test_branch_creation_help() {
    echo "Testing branch creation functionality documentation..."

    cd "${TNP_MOCK_REPO_PATH}"

    # Test that help mentions branch creation
    local help_output
    help_output=$(bash "${TNP_PATH}"/configure_github_branch_protection.bash --help)

    if [[ "$help_output" =~ "release and bleeding edge branches" ]]; then
        n2st::print_msg_done "✓ Branch creation functionality is documented"
    else
        n2st::print_msg_error "✗ Branch creation functionality not documented"
        return 1
    fi
}

function tnp::test_dry_run_functionality() {
    echo "Testing dry-run functionality..."

    cd "${TNP_MOCK_REPO_PATH}"

    # Test dry-run mode
    if bash "${TNP_PATH}"/configure_github_branch_protection.bash --dry-run --branch main; then
        n2st::print_msg_done "✓ Dry-run functionality works"
    else
        n2st::print_msg_error "✗ Dry-run functionality failed"
        return 1
    fi
}


function tnp::test_both_branches_default() {
    echo "Testing both branches configured by default..."

    cd "${TNP_MOCK_REPO_PATH}"

    # Test that both branches are configured by default
    local output
    output=$(bash "${TNP_PATH}"/configure_github_branch_protection.bash --dry-run)

    if [[ "$output" =~ "Processing branch: main" ]] && [[ "$output" =~ "Processing branch: dev" ]]; then
        n2st::print_msg_done "✓ Both branches configured by default"
    else
        n2st::print_msg_error "✗ Not both branches configured by default"
        return 1
    fi
}

function tnp::test_releaserc_json_update() {
    echo "Testing .releaserc.json update functionality..."

    cd "${TNP_MOCK_REPO_PATH}"

    # Test .releaserc.json update in dry-run mode
    local output
    output=$(bash "${TNP_PATH}"/configure_github_branch_protection.bash --dry-run --release-branch master)

    # shellcheck disable=SC2076
    if [[ "$output" =~ "DRY RUN: Would update .releaserc.json:" ]] && [[ "$output" =~ "Release branch: master" ]]; then
        n2st::print_msg_done "✓ .releaserc.json update functionality works"
    else
        n2st::print_msg_error "✗ .releaserc.json update functionality failed"
        return 1
    fi
}

function tnp::test_semantic_release_yml_update() {
    echo "Testing semantic_release.yml update functionality..."

    cd "${TNP_MOCK_REPO_PATH}"

    # Test semantic_release.yml update in dry-run mode
    local output
    output=$(bash "${TNP_PATH}"/configure_github_branch_protection.bash --dry-run --release-branch master)

    # shellcheck disable=SC2076
    if [[ "$output" =~ "DRY RUN: Would update .github/workflows/semantic_release.yml:" ]] && [[ "$output" =~ "Release branch: master" ]]; then
        n2st::print_msg_done "✓ semantic_release.yml update functionality works"
    else
        n2st::print_msg_error "✗ semantic_release.yml update functionality failed"
        return 1
    fi
}

function tnp::test_branch_renaming_functionality() {
    echo "Testing branch renaming functionality..."

    cd "${TNP_MOCK_REPO_PATH}"

    # Test branch renaming in dry-run mode
    local output
    output=$(bash "${TNP_PATH}"/configure_github_branch_protection.bash --dry-run --release-branch master)

    # shellcheck disable=SC2076
    if [[ "$output" =~ "DRY RUN: Would rename branch 'main' to 'master'" ]]; then
        n2st::print_msg_done "✓ Branch renaming functionality works"
    else
        n2st::print_msg_error "✗ Branch renaming functionality failed"
        return 1
    fi
}

function tnp::test_branch_renaming_documentation() {
    echo "Testing branch renaming functionality documentation..."

    cd "${TNP_MOCK_REPO_PATH}"

    # Test that help mentions branch renaming
    local help_output
    help_output=$(bash "${TNP_PATH}"/configure_github_branch_protection.bash --help)

    if [[ "$help_output" =~ "Branch handling:" ]] && [[ "$help_output" =~ "renamed to the specified release branch name" ]]; then
        n2st::print_msg_done "✓ Branch renaming functionality is documented"
    else
        n2st::print_msg_error "✗ Branch renaming functionality not documented"
        return 1
    fi
}

function tnp::main() {
    echo "Starting GitHub branch protection integration tests..."

    # ....Setup....................................................................................
    TNP_PATH=$(git rev-parse --show-toplevel)
    export TNP_PATH

    # ....Load environment variables from file.......................................................
    cd "${TNP_PATH}" || exit 1
    set -o allexport
    source .env.template-norlab-project.template
    set +o allexport

    source "${N2ST_PATH:?'Variable not set'}/import_norlab_shell_script_tools_lib.bash" || exit 1

    n2st::norlab_splash "${PROJECT_GIT_NAME}" "${PROJECT_GIT_REMOTE_URL}"

    n2st::print_formated_script_header "$(basename $0)" "="

    bash "${TNP_PATH}/tests/setup_mock.bash"
    bash "${TNP_PATH:?err}/tests/setup_integration_test.bash"

    export TNP_MOCK_REPO_PATH="${TNP_PATH:?err}/utilities/tmp/dockerized-norlab-project-mock-EMPTY"

    # ....Begin....................................................................................

    declare -i fct_exit_code=0

    tnp::test_prerequisites_validation || ((fct_exit_code++))
    tnp::test_help_output || ((fct_exit_code++))
    tnp::test_argument_parsing || ((fct_exit_code++))
    tnp::test_custom_branch_names || ((fct_exit_code++))
    tnp::test_branch_creation_help || ((fct_exit_code++))
    tnp::test_dry_run_functionality || ((fct_exit_code++))
    tnp::test_both_branches_default || ((fct_exit_code++))
    tnp::test_releaserc_json_update || ((fct_exit_code++))
    tnp::test_semantic_release_yml_update || ((fct_exit_code++))
    tnp::test_branch_renaming_functionality || ((fct_exit_code++))
    tnp::test_branch_renaming_documentation || ((fct_exit_code++))

    # ....Teardown.................................................................................
    bash "${TNP_PATH}/tests/teardown_integration_test.bash"
    bash "${TNP_PATH}/tests/teardown_mock.bash"

    if [[ ${fct_exit_code} == 0 ]]; then
      n2st::print_msg_done "${MSG_DONE_FORMAT}All dry-run tests completed successfully!${MSG_END_FORMAT}"
    else
      n2st::print_msg_error "${MSG_ERROR_FORMAT}Dry-run tests completed with failure!${MSG_END_FORMAT}"
    fi
    n2st::print_formated_script_footer "$(basename $0)" "="
    return ${fct_exit_code}
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    tnp::main "$@"
    exit $?
fi
