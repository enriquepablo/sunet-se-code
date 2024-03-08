#!/usr/bin/env bash
# template from https://betterprogramming.pub/my-minimal-safe-bash-script-template-300759114040
#
set -o errexit
set -o nounset
set -o pipefail

readonly error_reading_conf_file=2
readonly error_parsing_options=22
readonly error_no_jq_command=2

readonly script_name="${0##*/}"

readonly tmpfile1="/tmp/tickets1.json"
readonly tmpfile2="/tmp/tickets2.json"

trap clean_up ERR EXIT SIGINT SIGTERM

usage() {
    cat <<USAGE_TEXT
Usage: ${script_name} [-h | --help] [-f <configfile>] [-p <SUNET_JIRA_PASSWORD>]

DESCRIPTION

    Get JIRA tickets to be shown at sunet.se

OPTIONS:

-h, --help
        Print this help and exit.
-f
        Path to the configuration file. See the companion "get-jira-issues.conf.example" for details.
        If not provided, the script will attempt to read ./get-jira-issues.conf
-p
        JIRA password

USAGE_TEXT
}

clean_up() {
  trap - ERR EXIT SIGINT SIGTERM
  rm -f "$tmpfile1"
  rm -f "$tmpfile2"
}

die() {
  local -r msg="${1}"
  local -r code="${2:-90}"
  echo "${msg}" >&2
  exit "${code}"
}

parse_user_options() {
    local -r args=("${@}")
    local opts
    opts=$(getopt --options p:,f:,h --long help -- "${args[@]}" 2> /dev/null) || {
        usage
        die "error: parsing options" "${error_parsing_options}"
    }
    eval set -- "${opts}"
while true; do
    case "${1}" in
-f)
            readonly conf_file="${2}"
            shift
            shift
            ;;
-p)
            SUNET_JIRA_PASSWORD="${2}"
            shift
            shift
            ;;
--help|-h)
            usage
exit 0
            shift
            ;;
*)
            break
            ;;
    esac
    done
}

# function: join_array
# Join array given as 2nd arg with separator given as 1st arg
#
join_array() {
  local IFS="$1"
  shift
  echo "$*"
}

# function: external_comment_ids.
# First, retrieve all comments to the JIRA issue identified by the ID given as parameter.
# The comments here come with their properties, that tell us whether they are internal comments.
# Then we use jq to, 1st, filter out comments that have null properties,
# and 2nd to obtain the list of comment IDs that are not internal.
#
external_comment_ids() {
  local -r issueid="$1"
  issue_url="$baseurl/issue/${issueid}/comment?expand=properties"
  
  jq_remove_null_properties=".comments[] | select(.properties != null)"
  jq_select_external='select(.properties | map( .key == "sd.public.comment" and .value.internal == false ) | any) | .id'
  
  curl -s -XGET -H "Accept: application/json" -u "$username:$password" "$issue_url" | jq "$jq_remove_null_properties" | jq "$jq_select_external"
}

# check that the executable jq exists
if ! command -v jq &> /dev/null
then
    die "this script needs to have the jq executable available" "${error_no_jq_command}"
fi

# Parse CLI options
parse_user_options "${@}"

# Read configuration
config_file=${conf_file:-'get-jira-issues.conf'}
if [[ ! -f "${config_file}" ]]; then
    usage
    printf "\n\n"
    die "error reading configuration file: ${config_file}" "${error_reading_conf_file}"
fi
# shellcheck source=./get-jira-issues.conf.example
source "${config_file}"

baseurl="$JIRA_BASEURL"
username="$JIRA_USERNAME"
password=${SUNET_JIRA_PASSWORD:-$JIRA_PASSWORD}
output="$JIRA_TICKETS_OUTPUT"
project="$JIRA_PROJECT"
daysold="$MAX_CLOSED_AGE"

# JQL query to obtain all tickets belonging to project TIC that are open or were closed less that a configurable time (MAX_CLOSED_AGE) ago.
jql="\"jql\": \"project = $project and (resolutiondate is empty or resolutiondate > \\\"-$daysold\\\")\""

# JIRA spec to select the issue fields to retrieve
fields='"fields": ["issuekey", "issuetype", "status", "summary", "customfield_11800", "created", "resolutiondate", "customfield_11603", "customfield_10402", "customfield_11600", "description", "customfield_11802", "customfield_10405", "customfield_10403", "customfield_11601", "customfield_11604", "customfield_10404", "comment"]'
# Data to send to JIRA to retrieve the tickets 
data="{$jql, $fields}"

# JIRA API search endpoint
searchurl="$baseurl/search"

# jq to select tickets in which the field customfield_11600 is not null
jq_remove_null=".issues[] | select(.fields.customfield_11600 != null)"
# jq to select tickets in which the field customfield_11600 includes items starting with "affected_customer"
jq_select_ac='select(.fields.customfield_11600 | map( test("^affected_customer")) | any)'

# get all JIRA tickets
curl_output=$(curl -s -X POST --write-out "%{http_code}" --output "$tmpfile1" -H "Content-Type: application/json" -u "$username:$password" -d "$data" "$searchurl")

if [ "$curl_output" != "200" ]; then
    die "error response from JIRA: ${curl_output}" "${curl_output}"
fi

# get all tickets with affected customers and store them in a temp file
jq "$jq_remove_null" "$tmpfile1" | jq "$jq_select_ac" | jq -s "." > "$tmpfile2"


# Get the ticket IDs of all the tickets retrieved from JIRA
issue_ids=$(jq ".[].id | tonumber" "$tmpfile2")

# Retrive from JIRA all comments for the tickets gotten above (with additional info about them being internal),
# and produce a list with the IDs of all tickets not marked as internal.
all_comment_ids=()

for id in $issue_ids; do
  cids=$(external_comment_ids "$id")
  for cid in $cids; do
    all_comment_ids+=("$cid")
  done
done
comment_ids=$(join_array , "${all_comment_ids[@]}")

outfile="$output/tickets.json"

# jq to filter out internal comments from the tickets json
jq_remove_internal_comments="[ .[] | .fields.comment.comments |= map( select( [.id] | inside([${comment_ids}]) )) ]"
# jq_remove_internal_comments=".[].fields.comment.comments |= select( [.[].id] | inside([${comment_ids}]) )"  # this is for jq 1.6

# remove internal comments from tickets and place the resulting json in its final location
jq "$jq_remove_internal_comments" "$tmpfile2" > "$outfile"

exit 0
