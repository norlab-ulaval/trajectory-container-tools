#!/bin/bash
DOCUMENTATION_CONFIGURE_GITHUB_BRANCH_PROTECTION=$( cat <<'EOF'
# =================================================================================================
# Configure GitHub branch protection rules for release, pre-release and bleeding edge branches
#
# Usage:
#   $ bash configure_github_branch_protection.bash [OPTIONS]
#
# Options:
#   --release-branch BRANCH_NAME     Set release branch name (default: repository's default branch)
#   --dev-branch BRANCH_NAME         Set bleeding edge branch name (default: dev)
#   --branch BRANCH_NAME             Configure a specific branch only
#   --dry-run                        Show what would be done without making changes
#   --help                           Show this help message
#
# Notes:
#   - Require that the repository be hosted on GitHub
#   - Default branch name:
#     - Release branch: repository's default branch (automatically detected)
#     - Pre-release branch: 'beta'
#     - Bleeding edge branch: 'dev'
#   - Branch handling:
#     - If a non-default release branch name is specified and the repository's default branch exists,
#       the default branch will be renamed to the specified release branch name
#     - Otherwise, branches will be created and pushed to remote if they don't exist
#
# =================================================================================================
EOF
)
set -e

# ====Functions====================================================================================
function gbp::validate_prerequisites() {
    local repo_url
    n2st::print_msg "Validate pre-prerequisites"

    # Check if gh CLI is installed
    if ! command -v jq &> /dev/null; then
        n2st::print_msg_error "Command-line JSON processor (jq) is not installed. Please install it first:"
        echo "  https://manpages.ubuntu.com/manpages/focal/man1/jq.1.html"
        return 1
    fi

    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        n2st::print_msg_error "GitHub CLI (gh) is not installed. Please install it first:"
        echo "  https://cli.github.com/"
        return 1
    fi

    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        n2st::print_msg_error "GitHub CLI is not authenticated. Please run:"
        echo "  gh auth login"
        return 1
    fi

    # Check if current directory is a git repository
    if ! git rev-parse --git-dir &> /dev/null; then
        n2st::print_msg_error "Current directory is not a git repository"
        return 1
    fi

    # Check if repository is hosted on GitHub
    repo_url=$(git config --get remote.origin.url 2>/dev/null || echo "")
    if [[ ! "$repo_url" =~ github\.com ]]; then
        n2st::print_msg_error "Repository is not hosted on GitHub"
        return 1
    fi

    n2st::print_msg_done "Validate pre-prerequisites"
    return 0
}

function gbp::get_repository_info() {
    local repo_info
    repo_info=$(gh repo view --json "owner,name,defaultBranchRef")

    REPO_OWNER=$(echo "$repo_info" | jq -r '.owner.login')
    REPO_NAME=$(echo "$repo_info" | jq -r '.name')
    REPO_DEFAULT_BRANCH=$(echo "$repo_info" | jq -r '.defaultBranchRef.name')

    export REPO_OWNER
    export REPO_NAME
    export REPO_DEFAULT_BRANCH
    n2st::print_msg "Repository: ${REPO_OWNER}/${REPO_NAME} (default branch: ${REPO_DEFAULT_BRANCH})"
}

function gbp::rename_branch_if_needed() {
    local target_branch="$1"
    local dry_run="$2"
    local default_branch="${REPO_DEFAULT_BRANCH:-main}"

    # Only rename for non-default release branch names
    if [[ "${target_branch}" == "${default_branch}" ]]; then
        return 0
    fi

    # Check if default branch exists and target branch doesn't exist
    local default_exists=false
    local target_exists=false

    if git show-ref --verify --quiet "refs/heads/${default_branch}" || \
       git show-ref --verify --quiet "refs/remotes/origin/${default_branch}"; then
        default_exists=true
    fi

    if git show-ref --verify --quiet "refs/heads/${target_branch}" || \
       git show-ref --verify --quiet "refs/remotes/origin/${target_branch}"; then
        target_exists=true
    fi

    # Only rename if default exists and target doesn't exist
    if [[ "$default_exists" == "true" && "$target_exists" == "false" ]]; then
        if [[ "$dry_run" == "true" ]]; then
            n2st::print_msg "DRY RUN: Would rename branch '${default_branch}' to '${target_branch}'"
            return 0
        fi

        n2st::print_msg "Renaming branch '${default_branch}' to '${target_branch}'..."

        # Get current branch to restore later
        local current_branch
        current_branch=$(git branch --show-current)

        # Checkout the default branch if not already on it
        if [[ "$current_branch" != "${default_branch}" ]]; then
            if ! git checkout "${default_branch}"; then
                n2st::print_msg_error "Failed to checkout '${default_branch}' for renaming"
                return 1
            fi
        fi

        # Rename the branch locally
        if git branch -m "${target_branch}"; then

            # Push the new branch and delete the old one from remote
            if git push -u origin "${target_branch}"; then
                n2st::print_msg_done "Branch '${default_branch}' renamed to '${target_branch}'"

                # Update the default branch on GitHub if we're renaming the default
                if [[ "$dry_run" == "false" ]]; then
                    gh repo edit --default-branch "${target_branch}" 2>/dev/null || true
                fi

                # Delete old remote
                git push origin --delete "${default_branch}"

                # Remove reference to deleted remote branch
                git fetch --prune

                return 0
            else
                n2st::print_msg_error "Failed to update remote references for renamed branch"
                # Try to restore the original branch name
                git branch -m "${current_branch}" 2>/dev/null || true
                return 1
            fi
        else
            n2st::print_msg_error "Failed to rename branch '${default_branch}' to '${target_branch}'"
            return 1
        fi
    fi

    return 0
}

function gbp::create_branch_if_not_exists() {
    local branch_name="$1"
    local dry_run="$2"

    # Check if branch exists locally or remotely
    if git show-ref --verify --quiet "refs/heads/${branch_name}" || \
      git show-ref --verify --quiet "refs/remotes/origin/${branch_name}"; then
        n2st::print_msg "Branch '${branch_name}' already exists"
        return 0
    fi

    if [[ "$dry_run" == "true" ]]; then
        n2st::print_msg "DRY RUN: Would create branch '${branch_name}'"
        return 0
    fi

    n2st::print_msg "Creating branch '${branch_name}'..."

    # Create branch from current HEAD and push to remote
    if git checkout -b "${branch_name}" && git push -u origin "${branch_name}"; then
        n2st::print_msg_done "Branch '${branch_name}' created and pushed to remote"
        # Switch back to original branch
        git checkout -
    else
        n2st::print_msg_error "Failed to create branch '${branch_name}'"
        return 1
    fi
}

function gbp::configure_repository_settings() {
    local dry_run="$1"

    n2st::print_msg "Configuring repository-wide settings"

    declare -a gh_repo_edit_flags=(gh repo edit)
    gh_repo_edit_flags+=( --enable-auto-merge
                          --delete-branch-on-merge
                          --enable-merge-commit
                          --enable-squash-merge
                          --allow-update-branch
                          )

    if [[ "$dry_run" == "true" ]]; then
        n2st::print_msg "DRY RUN: Would configure repository with:"
        echo "${gh_repo_edit_flags[*]}"
        return 0
    fi

    # Apply repository-wide settings using gh repo edit
    if "${gh_repo_edit_flags[@]}" > /dev/null 2>&1; then
        n2st::print_msg_done "Repository-wide settings configured"
    else
        n2st::print_msg_error "Failed to configure repository-wide settings"
        return 1
    fi
}

function gbp::configure_branch_protection() {
    local branch_name="$1"
    local dry_run="$2"
    local protection_config

    n2st::print_msg "Configuring branch protection for: ${branch_name}"

    # Build protection configuration
    protection_config=$(cat <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": []
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true
}
EOF
    )

    if [[ "$dry_run" == "true" ]]; then
        n2st::print_msg "DRY RUN: Would configure ${branch_name} with:"
        echo "${protection_config}" | jq '.'
        return 0
    fi

    # Apply protection rule
    if gh api \
        --method PUT \
        --header "Accept: application/vnd.github+json" \
        "/repos/${REPO_OWNER:?err}/${REPO_NAME:?err}/branches/${branch_name}/protection" \
        --input <(echo "${protection_config}") > /dev/null; then
        n2st::print_msg_done "Branch protection configured for: ${branch_name}"
    else
        n2st::print_msg_error "Failed to configure branch protection for: ${branch_name}"
        return 1
    fi
}


function gbp::update_releaserc_json() {
    local release_branch="$1"
    local dry_run="$2"

    # Check if .releaserc.json exists
    if [[ ! -f ".releaserc.json" ]]; then
        n2st::print_msg_warning ".releaserc.json not found, skipping semantic-release configuration update"
        return 0
    fi

    # Only update if using non-default release branch name
    if [[ "${release_branch}" == "${REPO_DEFAULT_BRANCH:-main}" ]]; then
        n2st::print_msg "Using default release branch name, no .releaserc.json update needed"
        return 0
    fi

    n2st::print_msg "Updating .releaserc.json with custom release branch name..."

    if [[ "${dry_run}" == "true" ]]; then
        n2st::print_msg "DRY RUN: Would update .releaserc.json:"
        echo "  - Release branch: ${release_branch}"
        return 0
    fi

    # Create backup
    cp .releaserc.json .releaserc.json.backup

    # Update the branches configuration using jq
    local updated_config
    local jq_exit_code
    updated_config=$(jq --arg release_branch "${release_branch}" '
        .branches[0] = $release_branch
    ' .releaserc.json)
    jq_exit_code=$?

    if [[ ${jq_exit_code} -eq 0 ]]; then
        echo "${updated_config}" > .releaserc.json
        n2st::print_msg_done ".releaserc.json updated successfully"
        echo "Backup saved as .releaserc.json.backup"
    else
        n2st::print_msg_error "Failed to update .releaserc.json"
        # Restore backup
        mv .releaserc.json.backup .releaserc.json
        return 1
    fi
}

function gbp::update_semantic_release_yml() {
    local release_branch="$1"
    local dry_run="$2"

    # Check if semantic_release.yml exists
    if [[ ! -f ".github/workflows/semantic_release.yml" ]]; then
        n2st::print_msg_warning ".github/workflows/semantic_release.yml not found, skipping workflow update"
        return 0
    fi

    # Only update if using non-default release branch name
    if [[ "${release_branch}" == "${REPO_DEFAULT_BRANCH:-main}" ]]; then
        n2st::print_msg "Using default release branch name, no semantic_release.yml update needed"
        return 0
    fi

    n2st::print_msg "Updating semantic_release.yml with custom release branch name..."

    if [[ "$dry_run" == "true" ]]; then
        n2st::print_msg "DRY RUN: Would update .github/workflows/semantic_release.yml:"
        echo "  - Release branch: ${release_branch}"
        return 0
    fi

    # Create backup
    cp .github/workflows/semantic_release.yml .github/workflows/semantic_release.yml.backup

    # Update the branches configuration using sed
    local default_branch="${REPO_DEFAULT_BRANCH:-main}"
    if sed -i.tmp "s/- $default_branch/- ${release_branch}/g" .github/workflows/semantic_release.yml; then
        rm -f .github/workflows/semantic_release.yml.tmp
        n2st::print_msg_done "semantic_release.yml updated successfully"
        echo "Backup saved as .github/workflows/semantic_release.yml.backup"
    else
        n2st::print_msg_error "Failed to update semantic_release.yml"
        # Restore backup
        mv .github/workflows/semantic_release.yml.backup .github/workflows/semantic_release.yml
        return 1
    fi
}

function gbp::show_help() {
  # (NICE TO HAVE) ToDo: refactor as a n2st fct (ref NMO-583)
  echo -e "${MSG_DIMMED_FORMAT}"
  n2st::draw_horizontal_line_across_the_terminal_window "="
  echo -e "$0 --help\n"
  # Strip shell comment char `#` and both lines
  echo -e "${DOCUMENTATION_CONFIGURE_GITHUB_BRANCH_PROTECTION}" | sed '/\# ====.*/d' | sed 's/^\# //' | sed 's/^\#//'
  n2st::draw_horizontal_line_across_the_terminal_window "="
  echo -e "${MSG_END_FORMAT}"
}

function gbp::main() {
    local dry_run="false"
    local arbitrary_branch=""
    local release_branch=""
    local release_branch_specified="false"
    local pre_release_branch="beta"
    local dev_branch="dev"

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run="true"
                shift
                ;;
            --branch)
                arbitrary_branch="$2"
                shift 2
                ;;
            --release-branch)
                release_branch="$2"
                release_branch_specified="true"
                shift 2
                ;;
            --dev-branch)
                dev_branch="$2"
                shift 2
                ;;
            --help)
                gbp::show_help
                return 0
                ;;
            *)
                n2st::print_msg_error "Unknown option: $1"
                gbp::show_help
                return 1
                ;;
        esac
    done

    #n2st::norlab_splash "GitHub Branch Protection" "https://github.com/norlab-ulaval/template-norlab-project"
    #n2st::print_formated_script_header "$( basename $0)" "="

    # Validate prerequisites
    gbp::validate_prerequisites || return 1

    # Get repository information
    gbp::get_repository_info || return 1
    test -n "${REPO_OWNER:?err}" || n2st::print_msg_error_and_exit "Env variable REPO_OWNER need to be set and non-empty."
    test -n "${REPO_NAME:?err}" || n2st::print_msg_error_and_exit "Env variable REPO_NAME need to be set and non-empty."
    test -n "${REPO_DEFAULT_BRANCH:?err}" || n2st::print_msg_error_and_exit "Env variable REPO_DEFAULT_BRANCH need to be set and non-empty."

    # Configure repository-wide settings
    gbp::configure_repository_settings "${dry_run}" || return 1

    # Set release branch to repository default if not specified by user
    if [[ "$release_branch_specified" == "false" ]]; then
        release_branch="${REPO_DEFAULT_BRANCH:-main}"
        n2st::print_msg "Using repository default branch as release branch: ${release_branch}"
    fi

    # Configure branches
    if [[ -n "${arbitrary_branch}" ]]; then
        # Create branch if it doesn't exist
        gbp::create_branch_if_not_exists "${arbitrary_branch}" "${dry_run}" || return 1
        gbp::configure_branch_protection "${arbitrary_branch}" "${dry_run}" || return 1
    else
        # Try to rename the default branch to the release branch if needed
        gbp::rename_branch_if_needed "${release_branch}" "${dry_run}" || return 1

        # Update .releaserc.json if using non-default release branch name
        gbp::update_releaserc_json "${release_branch}" "${dry_run}" || return 1

        # Update semantic_release.yml if using non-default release branch name
        gbp::update_semantic_release_yml "${release_branch}" "${dry_run}" || return 1

        # Configure release and dev branches
        for branch in "${release_branch}" "${pre_release_branch}" "${dev_branch}"; do
            n2st::print_msg "Processing branch: ${branch}"
            # Create branch if it doesn't exist
            gbp::create_branch_if_not_exists "${branch}" "${dry_run}" || return 1
            # Configure protection
            gbp::configure_branch_protection "${branch}" "${dry_run}" || return 1
        done

    fi

    n2st::print_msg_done "Branch protection configuration completed"
    #n2st::print_formated_script_footer "$( basename $0)" "="
    return 0
}

# ====Main=========================================================================================
# Execute main function if script is run directly
tnp_error_prefix="\033[1;31m[TNP error]\033[0m"
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    arguments=( "$@" )
    if [[ -n ${N2ST_PATH}  ]] || [[ -d "${N2ST_PATH}/utilities/norlab-shell-script-tools" ]]; then
      :
    else
      echo -e "[TNP] The N2ST_PATH env var is not set! Assuming we are in stand alone mode"

      # ....Stand alone logic......................................................................
      super_project_path=$(git rev-parse --show-toplevel)

      if [[ ! -d "${super_project_path}/utilities/norlab-shell-script-tools"  ]]; then
        echo -e "[TNP] norlab-shell-script-tools is unreachable, cloning now in ${super_project_path}/utilities/norlab-shell-script-tools"
        mkdir -p "${super_project_path}/utilities"
        git submodule \
          add https://github.com/norlab-ulaval/norlab-shell-script-tools.git \
          "${super_project_path}/utilities/norlab-shell-script-tools"

        {
          _tmp_cwd=$(pwd)
          cd "${super_project_path}" || exit 1

          # Traverse the submodule recursively to fetch any sub-submodule
          git submodule update --remote --recursive --init

          # Commit the submodule to your repository
          git add .gitmodules
          git add utilities/norlab-shell-script-tools
          git commit -m 'Added norlab-shell-script-tools submodule to repository'

          cd "${_tmp_cwd}" || exit 1
          unset _tmp_cwd
        }
      fi

      export N2ST_PATH="${super_project_path}/utilities/norlab-shell-script-tools"
    fi

    # ....Load dependencies......................................................................
    source "${N2ST_PATH:?err}/import_norlab_shell_script_tools_lib.bash"

    # ....Execute branch configuration.............................................................
    gbp::main "${arguments[@]}"
    exit $?
else
   # This script is being sourced, ie: __name__="__source__"
   test -n "${N2ST_PATH}" || { echo -e "${tnp_error_prefix} The N2ST_PATH env var is not set!" 1>&2 && exit 1; }
   source "${N2ST_PATH:?err}/import_norlab_shell_script_tools_lib.bash"
fi
