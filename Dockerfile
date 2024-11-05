# Use an official Python runtime as a parent image
FROM python:3.11.9-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /code

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the Django project into the container
COPY . /code/

# Expose the port on which the Django app will run
EXPOSE 8000

# Run migrations and start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
