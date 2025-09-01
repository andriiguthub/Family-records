FROM python:3.9-alpine

WORKDIR /family

RUN apk update && apk upgrade && apk add sqlite unzip && \
        python -m pip install --root-user-action=ignore --upgrade pip && \
        pip3 install --root-user-action=ignore -r requirements.txt
RUN wget -O main.zip https://github.com/andylebedev/Family-records/archive/refs/heads/main.zip && \
        unzip main.zip && \
        mv Family-records-main/* /family/ && \
        rm -rf Family-records-main && \
        sqlite3 /family/familytree.db < db.init && \
        sqlite3 familytree.db ".tables"
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
