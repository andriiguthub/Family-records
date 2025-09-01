FROM python:3.9-alpine

WORKDIR /family

RUN apk add sqlite git && \
        git clone https://github.com/andylebedev/Family-records.git . && \
        pip3 install --root-user-action=ignore -r requirements.txt && \
        sqlite3 /family/familytree.db < db.init && \
        sqlite3 familytree.db ".tables"
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
