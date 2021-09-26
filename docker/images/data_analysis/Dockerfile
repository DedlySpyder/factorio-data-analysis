FROM dedlyspyder/factorio-headless-ubuntu:experimental

RUN apt-get update \
    && apt-get install -y \
        git \
        python3.8 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install requests

COPY scripts /scripts

RUN chmod +x /scripts/*

ENTRYPOINT ["/scripts/build_docs.py"]
