FROM python:3.8-slim-buster
LABEL maintainer="mailto@wolfbolin.com"

# Why need these step?
# - fast mirror source
# - procps contains useful proccess control commands like: free, kill, pkill, ps, top
# - wget is quite basic tool
# - vim for online debugging
# - sync timezone
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list \
	&& sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list \
	&& apt-get update && apt-get install -y --no-install-recommends procps wget vim \
	&& ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# Install google chrome
RUN wget -q -P /tmp https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y --no-install-recommends /tmp/google-chrome-stable_current_amd64.deb

# Set display port to avoid crash
ENV DISPLAY=:99

# Project environment
ENV SERVICE_ENV production

WORKDIR /usr/local/app
COPY . /usr/local/app
COPY ./Config/openssl.cnf /etc/ssl

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

CMD ["python","update_risk.py"]
