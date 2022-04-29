# start by pulling the python image
FROM python:3.8-slim

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip3 install -r requirements.txt
ENV lobkey=test_fb6400e1c0046839f9045b4ae957e5fd78d

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["flask_main.py" ]