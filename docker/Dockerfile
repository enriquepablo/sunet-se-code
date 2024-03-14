FROM debian:bookworm

ENV DEBIAN_FRONTEND noninteractive
ENV NGINX_VERSION 1.25.3.1

# required
ARG REFRESH_PASSWORD
ARG SUNET_JIRA_PASSWORD

# optional
ARG GITHUB_CODE_REPO="https://github.com/SUNET/sunet-se-code"
ARG GIT_BRANCH="staging"
ARG SERVER_NAME="sunet.se"
ARG REFRESH_USERNAME="editor"
ARG JIRA_BASEURL="https://jira-test.sunet.se/rest/api/2"
ARG JIRA_USERNAME="restsunetweb"
ARG JIRA_TICKETS_OUTPUT="/tmp"
ARG JIRA_PROJECT="TIC"
ARG MAX_CLOSED_AGE="30d"

ENV GITHUB_CODE_REPO=$GITHUB_CODE_REPO
ENV GIT_BRANCH=$GIT_BRANCH
ENV SERVER_NAME=$SERVER_NAME
ENV REFRESH_USERNAME=$REFRESH_USERNAME
ENV JIRA_BASEURL=$JIRA_BASEURL
ENV JIRA_USERNAME=$JIRA_USERNAME
ENV JIRA_TICKETS_OUTPUT=$JIRA_TICKETS_OUTPUT
ENV JIRA_PROJECT=$JIRA_PROJECT
ENV MAX_CLOSED_AGE=$MAX_CLOSED_AGE

# Install needed software

RUN apt-get -y update && apt-get -y upgrade && \
    apt-get install -y curl wget gnupg ca-certificates git nodejs \
    python3 python3-venv python3-pip npm openssl && \
    rm -rf /var/lib/apt/lists/*

RUN wget -O - https://openresty.org/package/pubkey.gpg | apt-key add -
RUN echo "deb http://openresty.org/package/debian bookworm openresty" \
    | tee /etc/apt/sources.list.d/openresty.list

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends openresty && \
    rm -rf /var/lib/apt/lists/*

RUN ls
RUN git clone --branch $GIT_BRANCH $GITHUB_CODE_REPO /opt/sunet-se-code

WORKDIR /opt/sunet-se-code

RUN git submodule init
RUN git submodule update

RUN python3 -m venv venv

RUN . venv/bin/activate && pip install -r requirements.txt
RUN npm install

RUN . venv/bin/activate && make pristine

RUN git config --global --add safe.directory /opt/sunet-se-code
RUN git config --global --add safe.directory /opt/sunet-se-code/sunet-se-content

COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY refresh.lua /usr/local/openresty/nginx/conf/refresh.lua
COPY update_site.sh /usr/local/bin/update_site.sh
COPY get-jira-issues.sh /usr/local/bin/get-jira-issues.sh
COPY get-jira-issues.conf /usr/local/bin/get-jira-issues.conf

RUN chmod 755 /usr/local/bin/update_site.sh
RUN chmod 755 /usr/local/bin/get-jira-issues.sh

RUN sed -i "s/SERVER_NAME/$SERVER_NAME/g" /usr/local/openresty/nginx/conf/nginx.conf
RUN sed -i "s/GIT_BRANCH/$GIT_BRANCH/g" /usr/local/bin/update_site.sh

RUN sed -i "s/SUNET_JIRA_PASSWORD/$SUNET_JIRA_PASSWORD/g" /usr/local/bin/update_site.sh

RUN sed -i "s|JIRA_BASEURL_PLACEHOLDER|$JIRA_BASEURL|g" /usr/local/bin/get-jira-issues.conf
RUN sed -i "s/JIRA_USERNAME_PLACEHOLDER/$JIRA_USERNAME/g" /usr/local/bin/get-jira-issues.conf
RUN sed -i "s|JIRA_TICKETS_OUTPUT_PLACEHOLDER|$JIRA_TICKETS_OUTPUT|g" /usr/local/bin/get-jira-issues.conf
RUN sed -i "s/JIRA_PROJECT_PLACEHOLDER/$JIRA_PROJECT/g" /usr/local/bin/get-jira-issues.conf
RUN sed -i "s/MAX_CLOSED_AGE_PLACEHOLDER/$MAX_CLOSED_AGE/g" /usr/local/bin/get-jira-issues.conf

RUN sh -c "echo -n '$REFRESH_USERNAME:' >> /usr/local/openresty/nginx/conf/.htpasswd"
RUN sh -c "openssl passwd -apr1 $REFRESH_PASSWORD >> /usr/local/openresty/nginx/conf/.htpasswd"

EXPOSE 80
	 
# Start OpenResty
CMD ["/usr/local/openresty/nginx/sbin/nginx", "-c", "/usr/local/openresty/nginx/conf/nginx.conf", "-g", "daemon off;"]
