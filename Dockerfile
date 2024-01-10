# Use a base image with Python
FROM python:3.9.13

# Install Chrome.
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update
RUN apt-get install -y google-chrome-stable

# Install ChromeDriver.
RUN wget -N https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/linux64/chromedriver-linux64.zip -P ~/
RUN unzip ~/chromedriver-linux64.zip -d ~/
RUN rm ~/chromedriver-linux64.zip
RUN mv -f ~/chromedriver-linux64 /usr/local/bin/chromedriver
RUN chmod +x /usr/local/bin/chromedriver


# copy any python requirements file into the install directory and install all python requirements.
COPY requirements.txt .
RUN pip3 install --upgrade --no-cache-dir -r /requirements.txt


WORKDIR /app
# Copy the rest of your application files
COPY . .

# Run your script
CMD ["python3", "app.py"]

