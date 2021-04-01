FROM python:3.8

ADD [ "https://dev.mysql.com/get/mysql-apt-config_0.8.16-1_all.deb", "/" ]

RUN apt-get -qq update \
	&& export DEBIAN_FRONTEND=noninteractive \
	&& apt-get -qq upgrade -y \
	&& apt-get -qq install -y --no-install-recommends \
		lsb-release \
		locales \
		build-essential \
		zlib1g-dev \
		python3-pycurl \
	# MySQL Tools
	&& dpkg -i /mysql-apt-config_0.8.16-1_all.deb \
	&& apt-get -qq update \
	&& apt-get -qq install -y --no-install-recommends \
		mysql-shell \
		mysql-client \
	# Clean up
	&& apt-get autoremove -y \
	&& apt-get clean -y \
	&& rm -rf /var/lib/apt/lists/* \
	&& rm mysql-apt-config*.deb

# Generate the en_US.UTF-8 locale used by mysqlsh
RUN sed -Ei 's/^# en_US\.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen

COPY ./setup/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --upgrade && pip install --upgrade pylint

# Create a new user dev (1000 matches the default user in WSL)
ARG USERNAME=rtbdev
ARG UID=1000
ARG GID=1000
RUN groupadd --gid $GID $USERNAME
RUN useradd --create-home --shell /bin/bash --uid $UID --gid $GID $USERNAME

# Run with dev user
USER $USERNAME
