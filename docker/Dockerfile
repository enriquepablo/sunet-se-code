FROM debian:bookworm

ENV DEBIAN_FRONTEND noninteractive

ENV GIT_BRANCH main
ENV SERVER_NAME localhost
ENV NGINX_VERSION=1.25.3.1

# Install needed software

RUN apt-get -y update && apt-get -y upgrade && \
    apt-get install -y curl wget gnupg ca-certificates git nodejs \
    python3 python3-venv python3-pip npm && \
    rm -rf /var/lib/apt/lists/*

RUN wget -O - https://openresty.org/package/pubkey.gpg | apt-key add -
RUN echo "deb http://openresty.org/package/debian bookworm openresty" \
    | tee /etc/apt/sources.list.d/openresty.list

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends openresty && \
    rm -rf /var/lib/apt/lists/*

RUN ls
RUN git clone --branch main https://github.com/enriquepablo/sunet-se-code /opt/sunet-se-code

WORKDIR /opt/sunet-se-code

RUN git submodule init
RUN git submodule update

RUN python3 -m venv venv
RUN . venv/bin/activate

RUN . venv/bin/activate && pip install -r requirements.txt
RUN npm install

RUN . venv/bin/activate && make pristine

COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY refresh.lua /usr/local/openresty/nginx/conf/refresh.lua

RUN sed -i 's/SERVER_NAME/$SERVER_NAME/g' /usr/local/openresty/nginx/conf/nginx.conf

EXPOSE 80
	 
# Start OpenResty
CMD ["/usr/local/openresty/nginx/sbin/nginx", "-c", "/usr/local/openresty/nginx/conf/nginx.conf", "-g", "daemon off;"]
