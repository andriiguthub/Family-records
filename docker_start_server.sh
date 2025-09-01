wget https://raw.githubusercontent.com/andylebedev/Family-records/main/Dockerfile
docker build --tag family-records . 
docker run -d -e API_KEY=test -v /apps/family/familytree.db:/family/familytree.db -p 15000:5000 family-records
