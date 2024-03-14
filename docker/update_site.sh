#!/bin/bash

log_file="/tmp/update_site.log"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$log_file"
}

# Base repository directory
repo_dir="/opt/sunet-se-code"

# Start logging
log "Update started."

# Ensure the script exits if any commands fail
set -e

# Change directory to repository base
cd "$repo_dir" || exit 1

# Pull changes from the remote origin
git pull &>> "$log_file"
log "Pulled changes from remote."

# Define GIT_BRANCH if not set
GIT_BRANCH=${GIT_BRANCH:-"staging"}  # Replace 'default_branch_name' with your branch

# Switch to content directory
cd "${repo_dir}/sunet-se-content" || exit 1

# Stash any local changes (optional, uncomment if needed)
# git stash push --include-untracked &>> "$log_file"

git fetch --all &>> "$log_file"
git reset --hard "origin/$GIT_BRANCH" &>> "$log_file"
git checkout "$GIT_BRANCH" &>> "$log_file"
git pull &>> "$log_file"
log "Updated content repository."

# Retrieve JIRA tickets
"${repo_dir}/get-jira-tickets.sh" -c get-jira-tickets.conf -p "$SUNET_JIRA_PASSWORD" &>> "$log_file"
log "Retrieved JIRA tickets."

# Activate virtual environment and build the site
source venv/bin/activate
make pristine &>> "$log_file"
log "Built the site."

log "Update completed successfully."

# Exit without error
exit 0
