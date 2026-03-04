FROM python:3.11-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    fonts-liberation \
    libasound2t64 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install matching ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') \
    && CHROME_MAJOR=$(echo $CHROME_VERSION | cut -d. -f1) \
    && echo "Chrome version: $CHROME_VERSION (major: $CHROME_MAJOR)" \
    && DRIVER_URL=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_MAJOR") \
    && echo "Driver version: $DRIVER_URL" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/$DRIVER_URL/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver* \
    && echo "ChromeDriver installed: $(chromedriver --version)"

# Set environment variables
ENV RENDER=true
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Set workdir
WORKDIR /app

# Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy app code
COPY . .

# Create reports directory
RUN mkdir -p reports

# Expose port
EXPOSE 10000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "300", "--workers", "2", "--threads", "4", "app:app"]
