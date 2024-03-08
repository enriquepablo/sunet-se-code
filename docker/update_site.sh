#!/bin/bash

# Change directory to /opt/web
cd /opt/sunet-se-code || exit 1

# Pull changes from the remote origin, including submodules
git pull --recurse-submodules origin main >/dev/null 2>&1
pull_status=$?

# activate virtualenv
source venv/bin/activate

# Run "make pristine" to build the site
make pristine >/dev/null 2>&1
make_status=$?

# If there were errors in either the git pull or make commands, return exit status 1
if [ $pull_status -ne 0 ] || [ $make_status -ne 0 ]; then
    exit 1
fi

# If there are no errors, return exit status 0
exit 0
