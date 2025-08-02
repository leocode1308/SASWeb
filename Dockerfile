# Set the python version as a build-time argument
# with Python 3.12 as the default
ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install os dependencies for our mini vm
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # for postgres
        libpq-dev \
        # for Pillow
        libjpeg-dev \
        # for CairoSVG
        libcairo2 \
        # other
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Create the mini vm's code directory
WORKDIR /app

# Copia los archivos de Pipenv al directorio de trabajo
COPY Pipfile* /app/

# Install pipenv first, then use it
RUN pip install --no-cache-dir pipenv \
    && pipenv install --system --skip-lock

ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}

ARG DJANGO_DEBUG=0
ENV DJANGO_DEBUG=${DJANGO_DEBUG}

# copy the project code into the container's working directory
COPY ./app /app

# database isn't available during build
# run any other commands that do not need the database
# such as:
RUN python manage.py vendor_pull
RUN python manage.py collectstatic --noinput

# whitenoise is used to serve static files in production
RUN pip install --no-cache-dir whitenoise

# set the Django default project name
ARG PROJ_NAME="app"

# create a bash script to run the Django project
# this script will execute at runtime when
# the container starts and the database is available
RUN printf "#!/bin/bash\n" > ./paracord_runner.sh && \
    printf "RUN_PORT=\"\${PORT:-8000}\"\n\n" >> ./paracord_runner.sh && \
    printf "python manage.py migrate --no-input\n" >> ./paracord_runner.sh && \
    printf "gunicorn ${PROJ_NAME}.wsgi:application --bind \"[::]:\$RUN_PORT\"\n" >> ./paracord_runner.sh

# make the bash script executable
RUN chmod +x paracord_runner.sh

# Clean up apt cache to reduce image size
RUN apt-get remove --purge -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Run the Django project via the runtime script
# when the container starts
CMD ./paracord_runner.sh