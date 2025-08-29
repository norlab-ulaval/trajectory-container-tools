#!/bin/bash
# =================================================================================================
# Configure this norlab project template
#
# Usage in a interactive terminal session:
#
#   $ cd <path/to/your/new/norlab/project/root/>
#   $ bash initialize_norlab_project_template.bash
#
# =================================================================================================
set -e            # exit on error
set -o pipefail   # exit if errors within pipes

MSG_DIMMED_FORMAT="\033[1;2m"
MSG_ERROR_FORMAT="\033[1;31m"
MSG_END_FORMAT="\033[0m"


function tnp::install_norlab_project_template(){
  local user_input
  local install_n2st
  local install_semantic_release
  local tmp_msg
  local script_path
  local tmp_root
  local repo_root_name
  script_path="$(realpath -q "${BASH_SOURCE[0]:-.}")"
  tmp_root="$(dirname "${script_path}")"
  repo_root_name="$(basename "${tmp_root}")"

  # ....Load environment variables from file.......................................................
  if [[ ! -f  ".env.template-norlab-project.template" ]]; then
    echo -e "${MSG_ERROR_FORMAT}[ERROR]${MSG_END_FORMAT} 'initialize_norlab_project_template.bash' script should be executed from the project root!\n Current working directory is '$(pwd)'" 1>&2
    return 1
  fi

  cd "${tmp_root}" || return 1
  set -o allexport
  source .env.template-norlab-project.template
  set +o allexport

  local new_project_git_name=${PROJECT_GIT_NAME:?err}

  # ....Source NorLab Project Template dependencies................................................

  source "${N2ST_PATH:?"Variable not set"}/import_norlab_shell_script_tools_lib.bash"
  source configure_github_branch_protection.bash

  # ....Pre-condition..............................................................................
  gbp::validate_prerequisites

  if ! command -v tree &> /dev/null; then
    n2st::print_msg_error "Directory visualization command 'tree' is not installed. Please install it first:"
    echo "See Requirements section -> https://github.com/norlab-ulaval/template-norlab-project?tab=readme-ov-file#requirements"
    echo "See Requirements section -> https://github.com/norlab-ulaval/template-norlab-project/blob/main/README.md#requirements"
    return 1
  fi

  # ====Begin======================================================================================

  n2st::norlab_splash "Norlab-Project-Template"  https://github.com/norlab-ulaval/template-norlab-project

  n2st::print_formated_script_header 'initialize_norlab_project_template.bash' '='

  # ....Force asking for password early............................................................
  cd "${tmp_root}" || return 1
  # ★ Note: Keep 'sudo', its required for preserving user interaction flow
  n2st::print_msg "Current repository structure
${MSG_DIMMED_FORMAT}
$(sudo tree -L 2 -a --noreport --dirsfirst -F -I .git -I .idea -I .cadence "${tmp_root}" | sed "s;^${tmp_root%/};${repo_root_name};" | sed 's/^/     /')
${MSG_END_FORMAT}"

  # ....Check branch protection feature repository compatibility...................................
  local branch_configuration_enable=true
  {
    local repo_is_private
    local repo_owner
    local repo_name
    repo_owner="$(gh repo view --json owner --jq '.owner.login')"
    repo_is_private="$(gh repo view --json isPrivate --jq '.isPrivate')"
    repo_name="$(gh repo view --json name --jq '.name')"
    #local repo_is_in_organization
    #repo_is_in_organization="$(gh repo view --json isInOrganization --jq '.isInOrganization')"

    if [[ ${repo_is_private} == true ]] && [[ ${repo_owner} != "norlab-ulaval" && ${repo_owner} != "vaul-ulaval" ]]; then
      n2st::print_msg_warning "${repo_name} is a private repository owned by ${repo_owner}.

  ${MSG_WARNING_FORMAT}Be advised, enabling branch protection rule on a private repository require a GitHub Pro plan${MSG_END_FORMAT}.

  Possible actions:
    Make repository visibility public ${MSG_DIMMED_FORMAT}-> (press 'P')${MSG_END_FORMAT}
    Skip branch configuration ${MSG_DIMMED_FORMAT}-> (press 'S')${MSG_END_FORMAT}
    Try it any way (I feel lucky) ${MSG_DIMMED_FORMAT}-> (press 'L')${MSG_END_FORMAT}
    Exit, change repo ownership to norlab-ulaval (or vaul-ulaval) and try again ${MSG_DIMMED_FORMAT}-> (press any other key)${MSG_END_FORMAT}
"
      unset user_input
      read -n 1 -r user_input
      echo
      if [[ "${user_input}" == "P" ]] || [[ "${user_input}" == "p" ]]; then
        n2st::print_msg "Changing repository visibility to public"
        gh repo edit --visibility public --accept-visibility-change-consequences > /dev/null || return 1
        n2st::print_msg "${repo_name} is now $(gh repo view --json visibility --jq '.visibility')"
      elif [[ "${user_input}" == "S" ]] || [[ "${user_input}" == "s" ]]; then
        n2st::print_msg "Will skip branch configuration"
        branch_configuration_enable=false
      elif [[ "${user_input}" == "L" ]] || [[ "${user_input}" == "l" ]]; then
        n2st::print_msg "Understood, you feel lucky ☘️"
        :
      else
        n2st::print_msg "Understood, see you back when repository ownership is switched to norlab-ulaval (or vaul-ulaval)."
        return 0
      fi
    fi
    
    
  }

  # ....Install NBS................................................................................
  {
    n2st::print_msg_awaiting_input "Do you want to install Norlab Build System (NBS) submodule?"
    echo
    tmp_msg="(press 'Y' to install, or press any other key to skip) "
    n2st::echo_centering_str "${tmp_msg}" "\033[2m" " "
    unset user_input
    read -n 1 -r user_input
    echo

    cd "${tmp_root}" || return 1
    if [[ "${user_input}" == "Y" ]] || [[ "${user_input}" == "y" ]]; then
      n2st::print_msg "Installing NBS"

      git submodule \
        add https://github.com/norlab-ulaval/norlab-build-system.git \
        utilities/norlab-build-system

      # Traverse the submodule recursively to fetch any sub-submodule
      git submodule update --remote --recursive --init

      n2st::seek_and_modify_string_in_file "#NBS_PATH=" "NBS_PATH=" .env.template-norlab-project.template
      n2st::seek_and_modify_string_in_file "#NBS_SPLASH_NAME=" "NBS_SPLASH_NAME=" .env.template-norlab-project.template

      # Commit the submodule to your repository
      git add .gitmodules
      git add utilities/norlab-build-system
      git add .env.template-norlab-project.template
      git commit -m 'build: Added norlab-build-system submodule to repository'

    else
      n2st::print_msg "Skipping NBS install"
      n2st::seek_and_modify_string_in_file "#NBS_PATH=.*" " " .env.template-norlab-project.template
      n2st::seek_and_modify_string_in_file "#NBS_SPLASH_NAME=.*" " " .env.template-norlab-project.template

    fi
  }

  # ....Install N2ST...............................................................................
  {
    n2st::print_msg_awaiting_input "Do you want to install Norlab Shell Script Tools (N2ST) submodule?"
    echo
    tmp_msg="(press 'Y' to install, or press any other key to skip) "
    n2st::echo_centering_str "${tmp_msg}" "\033[2m" " "
    unset user_input
    read -n 1 -r user_input
    echo

    install_n2st=true

    cd "${tmp_root}" || return 1
    if [[ "${user_input}" == "Y" ]] || [[ "${user_input}" == "y" ]]; then
      # Submodule is already pre-installed
      n2st::print_msg "Installing N2ST"

      mv tests/run_bats_core_test_in_n2st.template.bash tests/run_bats_core_test_in_n2st.bash

      n2st::seek_and_modify_string_in_file "Execute 'template-norlab-project.template' repo" "Execute '${new_project_git_name}' repo" tests/run_bats_core_test_in_n2st.bash
      n2st::seek_and_modify_string_in_file "source .env.template-norlab-project.template.*" "source .env.${new_project_git_name}" tests/run_bats_core_test_in_n2st.bash

    else
      n2st::print_msg "Skipping N2ST install"
      install_n2st=false
    fi
  }

  # ....Install Semantic-release...................................................................
  {
    n2st::print_msg_awaiting_input "Do you want to install Semantic-Release?"
    echo
    tmp_msg="(press 'Y' to install, or press any other key to skip) "
    n2st::echo_centering_str "${tmp_msg}" "\033[2m" " "
    unset user_input
    read -n 1 -r user_input
    echo

    if [[ "${user_input}" == "Y" ]] || [[ "${user_input}" == "y" ]]; then
      # Submodule is already pre-installed
      n2st::print_msg "Installing Semantic-Release"
      install_semantic_release=true

      n2st::print_msg "Resetting ${MSG_DIMMED_FORMAT}CHANGELOG.md${MSG_END_FORMAT}"
      cd "${tmp_root}" || return 1
      truncate -s 0 CHANGELOG.md

    else
      n2st::print_msg "Skipping Semantic-Release install"
      install_semantic_release=false

      rm -R version.txt
      rm -R CHANGELOG.md
      rm -R .releaserc.json
      rm -R .github/workflows/semantic_release.yml

    fi
  }

  # ....JetBrains files setup step.................................................................
  local install_jetbrains_resources
  {
    n2st::print_msg_awaiting_input "Do you want to install JetBrains IDE resources i.e., run configurations and Junie AI guidelines?"
    echo
    tmp_msg="(press 'Y' to install, or press any other key to skip) "
    n2st::echo_centering_str "${tmp_msg}" "\033[2m" " "
    unset user_input
    read -n 1 -r user_input
    echo

    cd "${tmp_root}" || return 1
    if [[ "${user_input}" == "Y" ]] || [[ "${user_input}" == "y" ]]; then
      n2st::print_msg "Installing JetBrains IDE resources"
      install_jetbrains_resources=true
    else
      n2st::print_msg "Skipping JetBrains IDE resources install"
      install_jetbrains_resources=false
    fi
  }

  # ....Modify project prefix......................................................................
  {
    n2st::print_msg_awaiting_input "Choose a project wide environment variable prefix? (keep it short, two to four letters, alpha numeric only and no spacing)"
    echo
    tmp_msg="(press 'return' when done) "
    n2st::echo_centering_str "${tmp_msg}" "\033[2m" " "
    echo
    unset user_input
    read -r user_input
    # echo "user_input=$user_input" # User user_input feedback
    echo

    # Capitalise new prefix
    local env_prefix
    local fct_prefix
    env_prefix="$(echo "${user_input}" | tr '[:lower:]' '[:upper:]')"
    fct_prefix="$(echo "${user_input}" | tr '[:upper:]' '[:lower:]')"

    n2st::print_msg "Using environment variable prefix ${MSG_DIMMED_FORMAT}${env_prefix}${MSG_END_FORMAT} e.g.: ${MSG_DIMMED_FORMAT}${env_prefix}_PATH${MSG_END_FORMAT}"

    cd "${tmp_root}" || return 1
    n2st::seek_and_modify_string_in_file "PLACEHOLDER_" "${env_prefix}_" .env.template-norlab-project.template
    n2st::seek_and_modify_string_in_file "PROJECT_PROMPT_NAME=Norlab-Project-Template" "PROJECT_PROMPT_NAME=${env_prefix}" .env.template-norlab-project.template

    mv .env.template-norlab-project.template ".env.${new_project_git_name}"


    n2st::seek_and_modify_string_in_file "folderName=\"\[TNP\]" "folderName=\"\[${env_prefix}\]" .run/open-a-terminal-in-ubuntu-container.run.xml
    n2st::seek_and_modify_string_in_file "folderName=\"\[TNP\]" "folderName=\"\[${env_prefix}\]" .run/run-Bats-Tests-All.run.xml

    if [[ ${install_n2st} == true ]]; then
      n2st::seek_and_modify_string_in_file "function n2st::" "function ${fct_prefix}::" src/dummy.bash
      n2st::seek_and_modify_string_in_file "n2st::" "${fct_prefix}::" tests/tests_bats/test_template.bats
      n2st::seek_and_modify_string_in_file "TNP_" "${env_prefix}_" tests/run_bats_core_test_in_n2st.bash
    fi

  }

  # ....Update code owners file....................................................................
  local git_user_name
  git_user_name="$(git config user.name)"

  {
    cd "${tmp_root}/.github" || return 1
    n2st::seek_and_modify_string_in_file "TNP_GIT_USER_NAME_PLACEHOLDER" "${git_user_name:-'TODO-CHANGE-GIT-NAME'}" CODEOWNERS
  }

  # ....Set main readme file.......................................................................
  {
    n2st::print_msg_awaiting_input "Which readme file you want to use? NorLab (Default) or VAUL"
    echo
    tmp_msg="(press 'V' to use VAUL, or press any other key to use NorLab) "
    n2st::echo_centering_str "${tmp_msg}" "\033[2m" " "
    unset user_input
    read -n 1 -r user_input
    echo

    cd "${tmp_root}" || return 1
    if [[ ${user_input} == "V" ]] || [[ ${user_input} == "v" ]]; then

      n2st::print_msg "Setting up the VAUL README.md"
      mv README.md "${tmp_root}/to_delete/NORLAB_PROJECT_TEMPLATE_INSTRUCTIONS.md"
      mv README.vaul_template.md README.md

      n2st::seek_and_modify_string_in_file "img.shields.io/github/v/release/vaul-ulaval/template-norlab-project" "img.shields.io/github/v/release/${repo_owner}/${new_project_git_name}" README.md
      n2st::seek_and_modify_string_in_file "vaul-ulaval/template-norlab-project.git" "${repo_owner}/${new_project_git_name}.git" README.md

      rm README.norlab_template.md

    else

      n2st::print_msg "Setting up the NorLab README.md"
      mv README.md "${tmp_root}/to_delete/NORLAB_PROJECT_TEMPLATE_INSTRUCTIONS.md"
      mv README.norlab_template.md README.md

      n2st::seek_and_modify_string_in_file "img.shields.io/github/v/release/norlab-ulaval/template-norlab-project" "img.shields.io/github/v/release/${repo_owner}/${new_project_git_name}" README.md
      n2st::seek_and_modify_string_in_file "norlab-ulaval/template-norlab-project.git" "${repo_owner}/${new_project_git_name}.git" README.md

      rm README.vaul_template.md

    fi

    n2st::seek_and_modify_string_in_file "https://github.com/TNP_GIT_USER_NAME_PLACEHOLDER\">TNP_GIT_USER_NAME_PLACEHOLDER" "https://github.com/${git_user_name:-'TODO-CHANGE-MAINTAINER'}\">${git_user_name:-'TODO-CHANGE-MAINTAINER'}" README.md
    n2st::seek_and_modify_string_in_file "TNP_PROJECT_NAME_PLACEHOLDER" "${new_project_git_name}" README.md

  }

  # ....Commit project configuration steps.........................................................
  {
    n2st::print_msg "Commit project configuration changes"
    cd "${tmp_root}" || return 1
    git add .
    git commit -m 'refactor: NorLab project template configuration'
  }

  # ....Configure GitHub branch protection.....................................................
  local release_branch="main"
  local dev_branch="dev"
  if [[ ${branch_configuration_enable} == true ]]; then
  {
    declare -a gbp_args=()

    n2st::print_msg_awaiting_input "Do you want to configure custom branch names for GitHub branch protection rule?"
    echo "  Default branch names:"
    echo "  - release branch: 'main'"
    echo "  - bleeding edge branch: 'dev'"
    echo "  - pre-release branch: 'beta' (not customizable)"
    echo
    tmp_msg="(press 'Y' to configure custom names) "
    n2st::echo_centering_str "${tmp_msg}" "\033[2m" " "
    tmp_msg="(press any other key to use defaults: main/dev) "
    n2st::echo_centering_str "${tmp_msg}" "\033[2m" " "
    unset user_input
    read -n 1 -r user_input
    echo

    if [[ "${user_input}" == "Y" ]] || [[ "${user_input}" == "y" ]]; then
      n2st::print_msg "Configuring custom branch names..."
      echo

      # Prompt for release branch name
      n2st::print_msg_awaiting_input "Enter the release branch name (default: main):"
      tmp_msg="(press 'return' when done) "
      n2st::echo_centering_str "${tmp_msg}" "\033[2m" " "
      unset user_input
      read -r user_input
      echo
      if [[ -n "${user_input}" ]]; then
        release_branch="${user_input}"
      fi
      echo

      # Prompt for dev branch name
      n2st::print_msg_awaiting_input "Enter the bleeding edge branch name (default: dev):"
      tmp_msg="(press 'return' when done) "
      n2st::echo_centering_str "${tmp_msg}" "\033[2m" " "
      unset user_input
      read -r user_input
      echo
      if [[ -n "${user_input}" ]]; then
        dev_branch="${user_input}"
      fi
      echo

      n2st::print_msg "Using custom branch names:"
      echo "  - release branch: '${release_branch}'"
      echo "  - bleeding edge branch: '${dev_branch}'"
      gbp_args=(--release-branch "${release_branch}" --dev-branch "${dev_branch}")
    else
      n2st::print_msg "Using default branch names:"
      echo "  - release branch: 'main'"
      echo "  - bleeding edge branch: 'dev'"
    fi
    echo
  }

    # ....Execute branch protection rule setup.....................................................
    gbp::main "${gbp_args[@]}" || return 1
  fi

  # ....Delayed N2ST deletion step.................................................................
  {
    cd "${tmp_root}" || return 1
    if [[ ${install_n2st} == false ]]; then

      # Delete N2ST submodule
      git rm utilities/norlab-shell-script-tools

      if [[ ! -d utilities/norlab-build-system ]]; then
        rm -R ".env.${new_project_git_name}"
      else
        n2st::seek_and_modify_string_in_file "N2ST_PATH=.*" " " ".env.${new_project_git_name}"
      fi

      rm -R src/dummy.bash
      rm -R ".run/run-Bats-Tests-All.run.xml"

      mkdir -p tests_FINAL
      mv tests/README.md tests_FINAL/README.md
      rm -R tests
      mv tests_FINAL tests

      n2st::print_msg "Commit N2ST lib deletion"
      git add src/dummy.bash
      if [[ ! -d utilities/norlab-build-system ]]; then
        git add ".env.${new_project_git_name}"
      fi
      git add tests
      git add ".run/run-Bats-Tests-All.run.xml"
      git commit -m 'build: Deleted norlab-shell-script-tools submodule from repository'
    fi
  }

  # ....Update ignore files........................................................................
  {
    n2st::seek_and_modify_string_in_file "# .*Dev required.*" " " ".gitignore"
    n2st::seek_and_modify_string_in_file "/utilities/tmp/dockerized-norlab-project-mock-EMPTY/" " " ".gitignore"
    n2st::seek_and_modify_string_in_file "/tests/.env.tnp_test_values" " " ".gitignore"
    git add ".gitignore"
  }

  # ....Setup Jetbrains related features...........................................................
  {
    cd "${tmp_root}" || return 1
    if [[ ${install_jetbrains_resources} == true ]] && [[ -d ~/PycharmProjects/ai_agent_guidelines ]] && [[ "$(whoami)" == "redleader" ]]; then
      rm -Rf ".junie"
      bash ~/PycharmProjects/ai_agent_guidelines/tools/initialize_super_project.bash "${tmp_root}"
      git add "${tmp_root}/.junie/"
    elif [[ ${install_jetbrains_resources} == true ]]; then
      rm -Rf ".junie"
      mkdir -p ".junie/active_plans"
      mkdir -p ".junie/ai_artifact"
      mkdir -p ".junie/ai_ignored"
      mkdir -p ".junie/ai_ignored/archive_plans"
      cat > ".junie/ai_ignored/scratch.md" <<EOF
# Prompt Redaction Scratch File

Is vcs ignore and AI ignore
@formatter:off

EOF
      cat > ".junie/ai_ignored/recipes.md" <<EOF
# Prompt Instruction Recipes

Is AI ignore
@formatter:off

EOF
      cat > ".junie/guidelines.md" <<'EOF'
# Repository Guidelines

## Repository Organization

- `.junie/` contains AI agent related files.
- `src/` contains repository source code.
- `tests/` contains tests files.
- `artifact/` contains project artifact such as experimental log, plot and rosbag.
- `utilities/` contains external libraries.

## General Instructions

- Unless explicitly mentioned otherwise:
  - Always put plan, report, summary and analysis document that are ready for review in the `.junie/ai_artifact` directory.
  - Put AI agent runtime generated artifact not related to implementation such as log file, temporary file or script output in the `.junie/ai_artifact` directory.

## Coding instructions

- Don't repeat yourself:
    - Use already implemented code whenever possible;
    - Leverage functionality provided by submodule and available libraries whenever possible.

## Testing Instructions

- Write tests who challenge the intended functionality or behavior.
- Write at least one test file per corresponding source code file.

## Version Control Instructions

- Never execute `git add` or `git commit` command. All changes made by AI agent require explicit
  code review and acceptance by the AI agent User before being commited to code base remote origin.

EOF
      # ....Update ai ignore files.................................................................
      n2st::seek_and_modify_string_in_file "# .*A2G related.*" " " ".aiignore"
      if grep -q "/.junie/ai_agent_guidelines/*" ".aiignore"; then
        n2st::seek_and_modify_string_in_file "/.junie/ai_agent_guidelines/*" " " ".aiignore"
      fi
      if grep -q "\!/.junie/ai_agent_guidelines/*" ".aiignore"; then
        n2st::seek_and_modify_string_in_file "\!/.junie/ai_agent_guidelines/*" " " ".aiignore"
      fi

      git add ".junie/"
      git add ".aiignore"
    else
      rm -Rf ".run/"
      rm -Rf ".junie/"
      rm -f ".aiignore"
      git add ".run/"
      git add ".junie/"
      git add ".aiignore"
    fi
  }

  # ====Teardown===================================================================================
  {
    n2st::print_msg "Teardown clean-up"
    cd "${tmp_root}" || return 1
    mv initialize_norlab_project_template.bash "to_delete/initialize_norlab_project_template.bash"
    if [[ ${branch_configuration_enable} == true ]]; then
      mv configure_github_branch_protection.bash "to_delete/configure_github_branch_protection.bash"
    fi
    git add "to_delete"

    rm -Rf "utilities/tmp"
    git add "utilities/tmp"

    if [[ ${install_n2st} == true ]]; then
      mkdir -p tests_FINAL/tests_bats/bats_testing_tools

      mv tests/run_bats_core_test_in_n2st.bash tests_FINAL/run_bats_core_test_in_n2st.bash
      mv tests/tests_bats/bats_testing_tools/bats_helper_functions_local.bash tests_FINAL/tests_bats/bats_testing_tools/bats_helper_functions_local.bash
      mv tests/tests_bats/test_template.bats tests_FINAL/tests_bats/test_template.bats

      rm -Rf tests
      mv tests_FINAL tests

      git add "tests"

    fi

    n2st::print_msg "Commit template-norlab-project files/dir clean-up"
    git commit -m 'build: Clean-up template-norlab-project from repository'

  }

  local remaining_config_steps_msg
  if [[ ${install_semantic_release} == true ]]; then
    remaining_config_steps_msg="Step 3 › Configure semantic-release GitHub token
         https://github.com/norlab-ulaval/template-norlab-project/tree/main#step-3--optional-configure-semantic-release-github-token-detailed
     -   Step 4 › Make it your own
         https://github.com/norlab-ulaval/template-norlab-project/tree/main##step-4--make-it-your-own-detailed"
  else
    remaining_config_steps_msg="${MSG_DIMMED_FORMAT}Step 3 › (skip) Configure semantic-release GitHub token${MSG_END_FORMAT}
     -   Step 4 › Make it your own
         https://github.com/norlab-ulaval/template-norlab-project/tree/main##step-4--make-it-your-own-detailed"
  fi

  echo
  n2st::draw_horizontal_line_across_the_terminal_window '='
  cd "${tmp_root}" || return 1
  n2st::print_msg_done "Repository initialization is complete.
   Your repository structure now look like this
${MSG_DIMMED_FORMAT}
$(tree -L 2 -a --noreport --dirsfirst -F -I .git -I .idea -I .cadence "${tmp_root}" | sed "s;^${tmp_root%/};${repo_root_name};" | sed 's/^/     /')
${MSG_END_FORMAT}
   You can delete the ${MSG_DIMMED_FORMAT}to_delete/${MSG_END_FORMAT} directory whenever you are ready.

   NorLab project remaining configuration steps:
     - ${MSG_DONE_FORMAT}✔ Step 1 › Generate the new repository${MSG_END_FORMAT}
     - ${MSG_DONE_FORMAT}✔ Step 2 › Execute initialize_norlab_project_template.bash${MSG_END_FORMAT}
     -   ${remaining_config_steps_msg}"
  if [[ ${branch_configuration_enable} == true ]]; then
    echo -e "
   Follow GitFlow branching scheme
                                                                 tag:release-1
     ── ${release_branch} ──────────────────────────────────────────────────────────┴────▶︎
          └─ ${dev_branch} ────────────────────────────────────────────────┴──────▶︎
                        └─ feature 1 ───┘    └─ feature 2 ───┘"
  fi
  echo
  echo "   Happy coding!"

  n2st::print_formated_script_footer 'initialize_norlab_project_template.bash' '='

  cd "${tmp_root}" || return 1
  return 0
}

# ::::Main:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  # This script is being run, ie: __name__="__main__"
  tnp::install_norlab_project_template
  exit $?
else
  # This script is being sourced, ie: __name__="__source__"
  echo -e "${MSG_ERROR_FORMAT}[ERROR]${MSG_END_FORMAT} This script must be run with bash i.e.: $ bash initialize_norlab_project_template.bash" 1>&2
  exit 1
fi

