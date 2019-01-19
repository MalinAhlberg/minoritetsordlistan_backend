FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y \
    python3 \
    vim \
    python3-pip


RUN mkdir -p /usr/src/app
COPY requirements.txt /usr/src/app/
WORKDIR /usr/src/app
RUN pip3 install -r requirements.txt
CMD ["python3", "route.py", "--develop"]
EXPOSE 4000
