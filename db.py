from flask import Flask
from flask_pymongo import PyMongo

app=Flask(__name__)

app.config['MONGO_DBNAME'] ='prs'
app.config['MONGO_URI'] ='mongodb+srv://shubh:shubh@prs-2b90z.mongodb.net/User?retryWrites=true'

mongo= PyMongo(app)

@app.route('/add')
def add():
        user=mongo.db.user
        user.insert({'name':'shubh'})
        return 'Added User'

if __name__ =='__main__':
    app.run(debug=True)
