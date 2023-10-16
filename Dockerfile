# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory
WORKDIR /app

RUN mkdir /app/logs

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Run main.py when the container launches
CMD ["python", "main.py"]

# CMD ["tail", "-f", "/dev/null"]