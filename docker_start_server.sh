wget -O Dockerfile https://raw.githubusercontent.com/andriiguthub/Family-records/refs/heads/main/Dockerfile
docker build --no-cache --progress=plain --tag family-records .
docker run -d -e API_KEY=test -v /apps/family/familytree.db:/family/familytree.db -p 80:5000 family-records
