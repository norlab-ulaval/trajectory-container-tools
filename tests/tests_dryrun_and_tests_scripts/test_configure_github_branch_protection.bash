#!/bin/bash
# =================================================================================================
# Integration test for GitHub branch protection configuration
# Note: This test requires a test repository and proper GitHub authentication
# =================================================================================================

set -e


function tnp::test_both_branches_default() {
    n2st::print_formated_script_header "Testing both branches configured with default name..." "/"

    bash "${TNP_PATH:?err}/tests/setup_integration_test.bash"

    cd "${TNP_MOCK_REPO_PATH}"

    local exit_code
    bash "${TNP_PATH}"/configure_github_branch_protection.bash
    exit_code=$?

    bash "${TNP_PATH}/tests/teardown_integration_test.bash"

    if [[ $exit_code == 0 ]]; then
        n2st::print_msg_done "✓ Both branches configured by default"
        return 0
    else
        n2st::print_msg_error "✗ Not both branches configured by default"
        return 1
    fi
}

function tnp::test_branches_rename_release() {
    n2st::print_formated_script_header "Testing branch renaming functionality (release)..." "/"

    bash "${TNP_PATH:?err}/tests/setup_integration_test.bash"

    cd "${TNP_MOCK_REPO_PATH}"

    local exit_code
    bash "${TNP_PATH}"/configure_github_branch_protection.bash --release-branch master
    exit_code=$?

    bash "${TNP_PATH}/tests/teardown_integration_test.bash" master

    if [[ $exit_code == 0 ]]; then
        n2st::print_msg_done "✓ Branch renaming functionality (release) works"
        return 0
    else
        n2st::print_msg_error "✗ Branch renaming functionality (release) failed"
        return 1
    fi
}

function tnp::test_branches_rename_bleeding() {
    n2st::print_formated_script_header "Testing branch renaming functionality (bleeding)..." "/"

    bash "${TNP_PATH:?err}/tests/setup_integration_test.bash"

    cd "${TNP_MOCK_REPO_PATH}"

    local exit_code
    bash "${TNP_PATH}"/configure_github_branch_protection.bash --dev-branch develop
    exit_code=$?

    bash "${TNP_PATH}/tests/teardown_integration_test.bash" develop

    if [[ $exit_code == 0 ]]; then
        n2st::print_msg_done "✓ Branch renaming functionality (bleeding) works"
        return 0
    else
        n2st::print_msg_error "✗ Branch renaming functionality (bleeding) failed"
        return 1
    fi
}

function tnp::test_setup_arbitrary_branch() {
    n2st::print_formated_script_header "Testing setup arbitrary branch..." "/"

    bash "${TNP_PATH:?err}/tests/setup_integration_test.bash"

    cd "${TNP_MOCK_REPO_PATH}"

    local exit_code
    bash "${TNP_PATH}"/configure_github_branch_protection.bash --branch feature1
    exit_code=$?

    bash "${TNP_PATH}/tests/teardown_integration_test.bash" feature1

    if [[ $exit_code == 0 ]]; then
        n2st::print_msg_done "✓ Setup arbitrary branch works"
        return 0
    else
        n2st::print_msg_error "✗ Setup arbitrary branch failed"
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

    export TNP_MOCK_REPO_PATH="${TNP_PATH:?err}/utilities/tmp/dockerized-norlab-project-mock-EMPTY"

    bash "${TNP_PATH}/tests/setup_mock.bash"

    # ....Begin....................................................................................
    declare -i fct_exit_code=0

    tnp::test_both_branches_default || ((fct_exit_code++))
    tnp::test_branches_rename_release || ((fct_exit_code++))
    tnp::test_branches_rename_bleeding || ((fct_exit_code++))
    tnp::test_setup_arbitrary_branch || ((fct_exit_code++))

    # ....Teardown.................................................................................
    bash "${TNP_PATH}/tests/teardown_mock.bash"

    if [[ ${fct_exit_code} == 0 ]]; then
      n2st::print_msg_done "${MSG_DONE_FORMAT}All end-to-end tests completed successfully!${MSG_END_FORMAT}"
    else
      n2st::print_msg_error "${MSG_ERROR_FORMAT}End-to-end tests completed with failure!${MSG_END_FORMAT}"
    fi
    n2st::print_formated_script_footer "$(basename $0)" "="
    return ${fct_exit_code}
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    tnp::main "$@"
    exit $?
fi
