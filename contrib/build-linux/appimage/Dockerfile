# Note: we deliberately use an old Debian stable as base image.
# "[AppImages] should be built on the oldest possible system, allowing them to run on newer systems"

FROM debian:buster@sha256:233c3bbc892229c82da7231980d50adceba4db56a08c0b7053a4852782703459

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Pin to a fixed snapshot date for reproducible builds
# Using December 1, 2024 (near end-of-life but still has latest patches)
RUN echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/20241201T000000Z buster main contrib non-free" > /etc/apt/sources.list \
 && echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20241201T000000Z buster/updates main contrib non-free" >> /etc/apt/sources.list \
 && echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/20241201T000000Z buster-updates main contrib non-free" >> /etc/apt/sources.list \
 && apt-get -o Acquire::Check-Valid-Until=false update \
 && apt-get install -y --no-install-recommends ca-certificates

# Install all build dependencies
RUN apt-get -o Acquire::Check-Valid-Until=false update && \
    apt-get install -qy --allow-downgrades \
        sudo \
        git \
        wget \
        make \
        autotools-dev \
        autoconf \
        libtool \
        autopoint \
        pkg-config \
        xz-utils \
        libssl-dev \
        libssl1.1 \
        openssl \
        zlib1g-dev \
        libffi-dev \
        libncurses5-dev \
        libncurses5 \
        libtinfo-dev \
        libtinfo5 \
        libsqlite3-dev \
        libusb-1.0-0-dev \
        libudev-dev \
        libudev1 \
        gettext \
        libdbus-1-3 \
        xutils-dev \
        libxkbcommon0 \
        libxkbcommon-x11-0 \
        libxcb1-dev \
        libxcb-xinerama0 \
        libxcb-randr0 \
        libxcb-render0 \
        libxcb-shm0 \
        libxcb-shape0 \
        libxcb-sync1 \
        libxcb-xfixes0 \
        libxcb-xkb1 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-util0 \
        libxcb-render-util0 \
        libxcb-cursor0 \
        libx11-xcb1 \
        libc6-dev \
        libc6 \
        libc-dev-bin \
        libv4l-dev \
        libjpeg62-turbo-dev \
        libx11-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get clean

RUN git config --global --add safe.directory '*'
