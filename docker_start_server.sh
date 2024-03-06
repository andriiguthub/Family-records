wget https://raw.githubusercontent.com/andylebedev/Family-records/main/Dockerfile
docker build --tag family-records . 
docker run -d -eAPI_KEY=test -v/family/familytree.db:/family/familytree.db -p15000:5000 family-records
