export FLASK_APP=backend
export FLASK_ENV=development
sudo systemctl start mongod.service
flask run