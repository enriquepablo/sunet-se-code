#!/bin/bash
#
touch update_site.log

# Change directory to /opt/web
cd /opt/sunet-se-code || exit 1

# Pull changes from the remote origin
git pull &>update_site.log
pull_status=$?

# Change directory to /opt/web
cd /opt/sunet-se-code/sunet-se-content || exit 1

git checkout GIT_BRANCH &>>update_site.log
git fetch --all &>>update_site.log
pull_status_2=$?

git reset --hard origin/GIT_BRANCH &>>update_site.log
git checkout GIT_BRANCH &>>update_site.log
git pull &>>update_site.log

cd ..

get-jira-tickets.sh -c get-jira-tickets.conf -p SUNET_JIRA_PASSWORD &>>update_site.log
tickets_status=$?

# activate virtualenv
source venv/bin/activate

# Run "make pristine" to build the site
make pristine &>>update_site.log
make_status=$?

# If there were errors in either the git pull or make commands, return exit status 1
if [ $pull_status -ne 0 ] || [ $pull_status_2 -ne 0 ] || [ $tickets_status -ne 0 ] || [ $make_status -ne 0 ]; then
    exit 1
fi

# If there are no errors, return exit status 0
exit 0
