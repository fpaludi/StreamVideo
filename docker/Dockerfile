FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Building ARGS
ARG INSTALL_DEV=false

# Install linux deps
RUN apt-get update -y && apt-get install ffmpeg libsm6 libxext6  -y

## Install python deps
RUN cd /app/
RUN python -m pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install -vv; else poetry install --no-dev -vv; fi"

## Update Workdir
WORKDIR /app/app/
COPY ./app/src/ .
CMD ["/start.sh"]
