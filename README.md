
# Cisco Coding Challange

# Setup
Create database to fetch the information from malware urls.

# first we need to clone our repository
 git clone <repository>
# create environment, which could ne containerized and perform the tasks as given below
 pyvenv codingchallange
 cd codingchallange
 source bin/activate
 pip install requirements.txt
# Setup the database
basically we can use relational or non-relational database here
    sqlite3 service.db
# import the csv format into db
    .mode csv service
    .import service.csv service
# Now Run urlservice.py
run http://localhost:5000
    0r
    /urlinfo/1/{host:port}/{uri}

which will return informations

Now a User can initiates the request and Proxy met with request which forward to web service, and service looks url in database.
Now, response will be generated and proxy can pass or block website
