# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install Poetry
RUN pip install poetry

# Use Poetry to install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["poetry", "run", "uvicorn", "stra2ics.app:APP", "--host", "0.0.0.0", "--port", "80"]
