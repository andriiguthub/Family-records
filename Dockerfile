FROM python:3.9-alpine

WORKDIR /family

RUN apk update && apk upgrade && apk add sqlite unzip && \
        python -m pip install --root-user-action --upgrade pip && \
        pip3 install --root-user-action -r requirements.txt
RUN wget https://github.com/andylebedev/Family-records/archive/refs/heads/main.zip && \
        unzip main.zip && \
        mv Family-records-main/* /family/ && \
        rm -rf Family-records-main && \
        sqlite3 familytree.db < db.init
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
