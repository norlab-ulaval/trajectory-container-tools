
rm -rf ".junie/ai_agent_guidelines"

# ====Norlab Project Template======================================================================

function norlab_project_template_directory_reset_check() {

    # ....Check project root directories...........................................................
    assert_dir_exist "/code/template-norlab-project"
    assert_dir_exist "${TEST_TEMP_DIR}/template-norlab-project"
    assert_equal $(pwd) "${TEST_TEMP_DIR}/template-norlab-project"

    # ....Check git related........................................................................
    assert_dir_exist .git
    assert_file_exist .gitmodules
    assert_file_exist .gitignore
    assert_file_exist commit_msg_reference.md
    assert_file_exist .github/CODEOWNERS
    assert_file_exist .github/pull_request_template.md

    # ....Check readme files.......................................................................
    assert_file_exist README.md
    assert_file_exist README.norlab_template.md
    assert_file_exist README.vaul_template.md

    # ....Check semantic-release related...........................................................
    assert_file_exist version.txt
    assert_file_exist CHANGELOG.md
    assert_file_exist .releaserc.json
    assert_file_exist .github/workflows/semantic_release.yml

    # ....Check tests related files/directory....................................................................
    assert_dir_exist tests/tests_bats/bats_testing_tools
    assert_file_exist tests/tests_bats/bats_testing_tools/bats_helper_functions_local.bash
    assert_file_exist tests/run_bats_core_test_in_n2st.template.bash
    assert_file_exist tests/run_bats_core_test_in_n2st.bash
    assert_file_exist tests/tests_bats/test_template.bats
    assert_file_exist src/dummy.bash
    assert_file_exist tests/tests_bats/bats_testing_tools/norlab_project_template_helper_functions.bash
    assert_file_exist tests/tests_bats/test_dotenv_files.bats
    assert_file_exist tests/tests_bats/test_initialize_norlab_project_template.bats

    # ....Check N2ST related.......................................................................
    assert_dir_exist utilities/norlab-shell-script-tools
    assert_file_contains .gitmodules "\[submodule \"utilities/norlab-shell-script-tools\"\]"
    assert_file_contains .gitmodules .*"url = https://github.com/norlab-ulaval/norlab-shell-script-tools.git"

    # ....Check NBS related........................................................................
    assert_dir_not_exist utilities/norlab-build-system
    assert_file_not_contains .gitmodules "\[submodule \"utilities/norlab-build-system\"\]"
    assert_file_not_contains .gitmodules "url = https://github.com/norlab-ulaval/norlab-build-system.git"

    # ....Check NorLab project template logic related..............................................
    assert_file_exist initialize_norlab_project_template.bash
    assert_file_exist configure_github_branch_protection.bash
    assert_file_exist .env.template-norlab-project.template
    assert_file_exist to_delete/README.md
    assert_file_not_exist NORLAB_PROJECT_TEMPLATE_INSTRUCTIONS.md
    assert_file_not_exist to_delete/NORLAB_PROJECT_TEMPLATE_INSTRUCTIONS.md
    assert_file_not_exist to_delete/initialize_norlab_project_template.bash
    assert_file_not_exist to_delete/configure_github_branch_protection.bash

    # ....Check dotenv content.....................................................................
    assert_file_contains .env.template-norlab-project.template "^PROJECT_PROMPT_NAME=Norlab-Project-Template"
    assert_file_contains .env.template-norlab-project.template "^#NBS_SPLASH_NAME=.*"
    assert_file_contains .env.template-norlab-project.template "^N2ST_PATH=\"\${PROJECT_PATH}/utilities/norlab-shell-script-tools\""
    assert_file_contains .env.template-norlab-project.template "^#NBS_PATH=\"\${PROJECT_PATH}/utilities/norlab-build-system\""
    assert_file_contains .env.template-norlab-project.template "^PLACEHOLDER_PROMPT_NAME.*"
    assert_file_contains .env.template-norlab-project.template "^PLACEHOLDER_GIT_REMOTE_URL.*"
    assert_file_contains .env.template-norlab-project.template "^PLACEHOLDER_GIT_NAME.*"
    assert_file_contains .env.template-norlab-project.template "^PLACEHOLDER_PATH.*"
    assert_file_contains .env.template-norlab-project.template "^PLACEHOLDER_SRC_NAME.*"


}

function check_NBS_is_installed() {
  cd "${BATS_DOCKER_WORKDIR}" || exit 1
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Installing NBS"
  assert_dir_exist utilities/norlab-build-system
  assert_file_contains .env.template-norlab-project "^NBS_PATH=\"\${PROJECT_PATH}/utilities/norlab-build-system\""
  assert_file_contains .env.template-norlab-project "^NBS_SPLASH_NAME=.*"
  assert_dir_not_exist utilities/tmp
}

function check_NBS_not_installed() {
  cd "${BATS_DOCKER_WORKDIR}" || exit 1
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Skipping NBS install"
  assert_dir_not_exist utilities/norlab-build-system
  assert_file_not_contains .env.template-norlab-project "^#NBS_PATH=\"\${PROJECT_PATH}/utilities/norlab-build-system\""
  assert_file_not_contains .env.template-norlab-project "^NBS_PATH=\"\${PROJECT_PATH}/utilities/norlab-build-system\""
  assert_file_not_contains .env.template-norlab-project "^NBS_SPLASH_NAME=.*"
  assert_dir_exist tests
  assert_dir_not_exist utilities/tmp
}

function check_N2ST_is_installed() {
  cd "${BATS_DOCKER_WORKDIR}" || exit 1
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Installing N2ST"
  assert_dir_exist utilities/norlab-shell-script-tools
  assert_file_contains .env.template-norlab-project "^N2ST_PATH=\"\${PROJECT_PATH}/utilities/norlab-shell-script-tools\""
  assert_file_exist src/dummy.bash
  assert_file_exist tests/run_bats_core_test_in_n2st.bash
  assert_file_exist tests/tests_bats/bats_testing_tools/bats_helper_functions_local.bash
  assert_file_exist tests/tests_bats/test_template.bats
  assert_dir_not_exist utilities/tmp

}

function check_N2ST_not_installed() {
  cd "${BATS_DOCKER_WORKDIR}" || exit 1
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Skipping N2ST install"
  assert_dir_not_exist utilities/norlab-shell-script-tools
  assert_file_not_contains .env.template-norlab-project "^N2ST_PATH=\"\${PROJECT_PATH}/utilities/norlab-shell-script-tools\""

  assert_file_not_exist src/dummy.bash
  assert_dir_exist tests
  assert_dir_not_exist tests/tests_bats
  assert_file_not_exist tests/run_bats_core_test_in_n2st.bash
  assert_dir_not_exist utilities/tmp
}

function check_no_submodule_installed() {
  cd "${BATS_DOCKER_WORKDIR}" || exit 1
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Skipping N2ST install"
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Skipping NBS install"
  assert_dir_not_exist utilities/norlab-shell-script-tools
  assert_dir_not_exist utilities/norlab-build-system
#  assert_file_not_contains .env.template-norlab-project "^N2ST_PATH=\"\${PROJECT_PATH}/utilities/norlab-shell-script-tools\""
  assert_file_not_exist .env.template-norlab-project

  assert_file_not_exist src/dummy.bash
  assert_dir_exist tests
  assert_dir_not_exist tests/tests_bats
  assert_file_not_exist tests/run_bats_core_test_in_n2st.bash
  assert_dir_not_exist utilities/tmp
}

function check_semantic_release_is_installed() {
  cd "${BATS_DOCKER_WORKDIR}" || exit 1
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Installing Semantic-Release"
  assert_file_exist version.txt
  assert_file_exist .releaserc.json
  assert_file_exist .github/workflows/semantic_release.yml
  assert_file_exist CHANGELOG.md
  assert_file_empty CHANGELOG.md
}

function check_semantic_release_not_installed() {
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Skipping Semantic-Release install"
  cd "${BATS_DOCKER_WORKDIR}" || exit 1
  assert_file_not_exist version.txt
  assert_file_not_exist CHANGELOG.md
  assert_file_not_exist .releaserc.json
  assert_file_not_exist .github/workflows/semantic_release.yml
}

function check_jetbrains_resources_is_installed() {
  cd "${BATS_DOCKER_WORKDIR}" || exit 1
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Installing JetBrains IDE resources"

  assert_dir_exist .run
  assert_file_exist .run/open-a-terminal-in-ubuntu-container.run.xml

  assert_dir_exist .junie
  assert_file_exist .junie/guidelines.md
  assert_dir_exist .junie/active_plans
  assert_dir_exist .junie/ai_ignored
  assert_file_exist .junie/ai_ignored/recipes.md
  assert_file_exist .junie/ai_ignored/scratch.md
  assert_file_exist .aiignore

  assert_file_not_contains ".aiignore" "A2G related"
  assert_file_not_contains ".aiignore" "ai_agent_guidelines"
  assert_file_not_contains ".aiignore" "^\*$"
  assert_file_not_contains ".aiignore" "^/$"

  assert_dir_not_exist .junie/ai_agent_guidelines
}

function check_jetbrains_resources_not_installed() {
  cd "${BATS_DOCKER_WORKDIR}" || exit 1
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Skipping JetBrains IDE resources install"
  assert_dir_not_exist .run
  assert_dir_not_exist .junie
  assert_file_not_exist .aiignore
  assert_dir_not_exist .junie/ai_agent_guidelines
}


function check_norlab_project_template_teardown() {
  assert_output --regexp .*"\[Norlab-Project-Template\]".*"Teardown clean-up"

  assert_output --regexp .*"\[Norlab-Project-Template done\]".*"Repository initialization is complete.".*"Your repository structure now look like this".*"You can delete the".*"to_delete/".*"directory whenever you are ready.".*"NorLab project remaining configuration steps:".*"-".*"✔ Step 1 › Generate the new repository".*"-".*"✔ Step 2 › Execute initialize_norlab_project_template.bash".*"-   Step 3".*"Make it your own".*"Happy coding".*"Completed"

  cd "${BATS_DOCKER_WORKDIR}" || exit 1

  # ....Check TNP tests related....................................................................
  assert_file_not_exist tests/run_bats_core_test_in_n2st.template.bash
  assert_file_not_exist tests/run_all_dryrun_and_tests_scripts.bash
  assert_dir_not_exist tests/tests_dryrun_and_tests_scripts

  assert_file_not_exist tests/tests_bats/bats_testing_tools/norlab_project_template_helper_functions.bash
  assert_file_not_exist tests/tests_bats/test_dotenv_files.bats
  assert_file_not_exist tests/tests_bats/test_initialize_norlab_project_template.bats

  assert_file_not_exist tests/setup_integration_test.bash
  assert_file_not_exist tests/setup_mock.bash
  assert_file_not_exist tests/teardown_integration_test.bash
  assert_file_not_exist tests/teardown_mock.bash

  # ....Check TNP post install related.............................................................
  assert_file_exist to_delete/NORLAB_PROJECT_TEMPLATE_INSTRUCTIONS.md
  assert_file_exist to_delete/initialize_norlab_project_template.bash
  assert_file_exist to_delete/configure_github_branch_protection.bash
  assert_file_not_exist NORLAB_PROJECT_TEMPLATE_INSTRUCTIONS.md
  assert_file_not_exist initialize_norlab_project_template.bash
  assert_file_not_exist configure_github_branch_protection.bash

}
