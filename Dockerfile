# FROM public.ecr.aws/lambda/python:3.10
FROM public.ecr.aws/lambda/python@sha256:0b8d0fa373384edace5d97e7f96e835fe43f065045a0bcb09e0dbc20fc33d351 as build
RUN yum install -y unzip && \
    curl -Lo "/tmp/chromedriver.zip" "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" && \
    curl -Lo "/tmp/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1135561%2Fchrome-linux.zip?alt=media" && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    unzip /tmp/chrome-linux.zip -d /opt/

FROM public.ecr.aws/lambda/python@sha256:0b8d0fa373384edace5d97e7f96e835fe43f065045a0bcb09e0dbc20fc33d351
RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel -y
# RUN pip install selenium==4.13.0
COPY --from=build /opt/chrome-linux /opt/chrome
COPY --from=build /opt/chromedriver /opt/

# WORKDIR /srv


# ADD . /srv
# RUN apt-get -y update
# RUN pip install --upgrade pip
# RUN apt-get install zip -y
# RUN apt-get install unzip -y

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# RUN yum install -y unzip && \
#     curl -Lo "/tmp/chromedriver.zip" "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" && \
#     curl -Lo "/tmp/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1135561%2Fchrome-linux.zip?alt=media" && \
#     unzip /tmp/chromedriver.zip -d /opt/ && \
#     unzip /tmp/chrome-linux.zip -d /opt/


# RUN apt-get update && apt-get install gnupg wget -y && \
#     wget --quiet --output-document=- https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /etc/apt/trusted.gpg.d/google-archive.gpg && \
#     sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' && \
#     apt-get update && \
#     apt-get install google-chrome-stable -y --no-install-recommends && \
#     rm -rf /var/lib/apt/lists/*
# RUN yum install -y wget unzip libX11
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm && \
#     yum install -y google-chrome-stable_current_x86_64.rpm

# RUN CHROME_DRIVER_VERSION=`curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
#     wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
#     unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

COPY app.py ./

# RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
#     libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
#     libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
#     xorg-x11-xauth dbus-glib dbus-glib-devel -y

# COPY --from=build /opt/chrome-linux /opt/chrome
# COPY --from=build /opt/chromedriver /opt/

# COPY chromedriver ./
COPY captcha_recognition_model.h5 ./

CMD ["app.lambda_handler"]