
# Content manager for sunet.se

This software is for managing the sunet.se site. It has to be installed in 2
different places: in the server that will host the site, and in the machine of
the editor that will manage the site.

There are 2 git repositories involved in this. [One is for the
content](https://github.com/SUNET/sunet-se-content) that holds the markdown
content as an obsidian vault, and the other is the present one, that has the
code to build the html site from the markdown in the content repo and to serve
it in a docker container.

## Installation on the server machine.

The service is run as a docker container, so we need docker in the machine that
will host the site.

There are 2 locations in this service: the public location that will serve the
static site, and a restricted location (protected with basic auth credentials)
offering the `/refresh-content` endpoint, which when accessed will trigger
fetching all the new content from the content repo and building it.

Clone the code repo and cd to the docker container:

```bash
$ git clone git@github.com:SUNET/sunet-se-code.git
$ cd sunet-se-code/docker
```

To build the docker image we need to provide it with a few build variables,
provided with `docker build --build-arg ...`.

Required variables:

- SUNET_JIRA_PASSWORD The password for the Sunet JIRA API to pull the tickets
  for the arenden section. Obtained from the JIRA operators.
- REFRESH_PASSWORD The basic auth password for the `/refresh-content` endpoint.
  This is created anew here, and then set (as desccribed below) in the editor's
  environment.

Optional variables:

- SERVER_NAME The hostname of the service, e.g. staging.sunet.se. Default "sunet.se"
- GITHUB_CODE_REPO: Github repo with the sunet.se code. Default
  "https://github.com/SUNET/sunet-se-code"
- GIT_BRANCH: the git branch of the content repo that will be used to build the
  site. Default "staging".
- REFRESH_USERNAME The basic auth username for the `/refresh-content` endpoint.
  Default "editor"
- JIRA_BASEURL: Base URL for the JIRA API. Default "https://jira-test.sunet.se/rest/api/2"
- JIRA_USERNAME: Username for the JIRA API. Default "restsunetweb".
- JIRA_PROJECT: JIRA projecct from which the tickets will be pulled. Default "TIC".
- MAX_CLOSED_AGE: Only retrieve closed tickets that were closed less than this
  number of days ago. Default "30d".

Example build command:

```bash
$ docker build --build-arg SUNET_JIRA_PASSWORD=secret1 --build-arg REFRESH_PASSWORD=secret2 -t sunet-se:latest .
```

Once the image is built, run it, for example with:

```bash
$ docker run -d -p 80:80 --name sunet sunet-se:latest
```

## Installation in the editor's machine.

The editor's machine needs to have git and obsidian installed.

Clone the content repo, and make sure that changes committed in the local clone
can be pushed to github. The obsidian plugin in charge of pushing changes
assumes that `git push` is already provided with credentials (e.g., via ssh)
and set to push to the staging branch.

```bash
$ git clone git@github.com:SUNET/sunet-se-content.git
```

Open obsidian, and look for "open folder as vault" (from "open another vault"),
and in the resulting dialog select the cloned repo.

Go to the obsidian settings, and under "community plugins" click on "Sunet
plugin". Here we have to enter the URL for the `refresh-content` endpoint of
the staging server (e.g. `https://staging.sunet.se/refresh-content`), and the
username and password that have been set in the staging server as
REFRESH_USERNAME and REFRESH_PASSWORD.

After this, the editor should be all set to start working on the site.
