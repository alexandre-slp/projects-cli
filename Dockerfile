FROM python:3-alpine as base

COPY requirements.txt /install/
WORKDIR install
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN rm -rf install
RUN addgroup -g 1000 -S nonroot
RUN adduser -u 1000 -S nonroot -G nonroot
USER nonroot

COPY app/. app/
WORKDIR app

ENTRYPOINT ["python", "main.py"]
CMD ["python", "main.py", "--help"]
