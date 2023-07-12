  git pull
  sudo docker rm -f app
  sudo docker build --memory 4g -t app .
  sudo docker run --name app -d -p 8000:8000 -p 27017:27017 -p 27016:27016 -p 27015:27015 app