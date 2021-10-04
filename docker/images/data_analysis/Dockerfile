FROM dedlyspyder/factorio-headless-ubuntu:experimental

RUN apt-get update \
    && apt-get install -y \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install requests

COPY scripts /scripts

RUN chmod +x /scripts/*

ENTRYPOINT ["/scripts/run_analysis.py"]
