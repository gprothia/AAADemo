# Test-runner image: Playwright (browsers preinstalled) + Python for the API suite.
# Keep the Playwright image tag in step with @playwright/test in tests/ui/package.json.
FROM mcr.microsoft.com/playwright:v1.65.0-noble

RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tests
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY ui/package.json ui/
RUN cd ui && npm install --no-audit --no-fund

COPY . .
RUN chmod +x run.sh
ENV CI=true REPORT_DIR=/reports
ENTRYPOINT ["/tests/run.sh"]
