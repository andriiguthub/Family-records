FROM python:3.9

WORKDIR /family

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN ls -la /family/
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
