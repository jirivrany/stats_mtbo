# Use the official Python image from the Docker Hub
FROM python:3.12-alpine

# Upgrade pip as root
RUN pip install --upgrade pip

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV USER_ID=1000
ENV GROUP_ID=1000
ENV USER_NAME=albert
ENV GROUP_NAME=albert
ENV FLASK_APP=flaskapp.py
ENV TZ="Europe/Prague"

# Install system dependencies
RUN apk add --update && apk add --no-cache bash curl gcc git mariadb-connector-c-dev mariadb-dev musl-dev vim

# Create a group and user 
RUN addgroup -g $GROUP_ID $GROUP_NAME && \
 adduser --shell /sbin/nologin --disabled-password \
  --uid $USER_ID --ingroup $GROUP_NAME $USER_NAME

# Create the working directory and set permissions for the user
RUN mkdir /app && chown $USER_NAME:$GROUP_NAME /app  

# Switch to the created user
USER $USER_NAME

# Set the working directory inside the container
WORKDIR /app

# Copy Python dependencies
COPY --chown=$USER_NAME:$USER_NAME ./requirements.txt /app/requirements.txt

# Install Python dependencies for the user
RUN pip install --user -r requirements.txt

# Add user bin to PATH
ENV PATH="/home/${USER_NAME}/.local/bin:${PATH}"

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the Flask development server in debug mode
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
