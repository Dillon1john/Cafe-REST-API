from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    ##Cafe TABLE Configuration
    class Cafe(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(250), unique=True, nullable=False)
        map_url = db.Column(db.String(500), nullable=False)
        img_url = db.Column(db.String(500), nullable=False)
        location = db.Column(db.String(250), nullable=False)
        seats = db.Column(db.String(250), nullable=False)
        has_toilet = db.Column(db.Boolean, nullable=False)
        has_wifi = db.Column(db.Boolean, nullable=False)
        has_sockets = db.Column(db.Boolean, nullable=False)
        can_take_calls = db.Column(db.Boolean, nullable=False)
        coffee_price = db.Column(db.String(250), nullable=True)

        # Optional: will allow each book object to be identified by its title when printed
        def _repr__(self):
            return f'<Cafe {self.title}'


        def to_dict(self):
            # Method 1
            dictionary = {}
            #Loop through each column in the data record
            for column in self.__table__.columns:
                #Create a new dictionary entry where the key is the name of the column and the value is the value of the column
                dictionary[column.name] = getattr(self, column.name)
            return dictionary
            # #Method 2: Alternatively use Dictionary Comprehensipn to fo the same thing.
            # return {column.name: getattr(self.column.name) for column in self.__table__.columns}



    @app.route("/")
    def home():
        return render_template("index.html")


    ## HTTP GET - Read Record
    @app.route('/random', methods=['GET'])
    def randomize():
        # # Get the total number of rows in the databse
        # row_count = db.session.query(Cafe).all().count()
        # # Generate a random number for skipping some records
        # random_offset = random.randint(0, row_count - 1)
        # # Return the first record after skipping random_offset rows
        # random_cafe = db.session.query(Cafe).offset(random_offset).first()
        cafes = db.session.query(Cafe).all()
        random_cafe = random.choice(cafes)
        #Simply convert the random_cafe data record to a dictionary of key-value
        return jsonify(cafe=random_cafe.to_dict())

    @app.route('/all', methods=['GET'])
    def get_all_cafes():
        cafes = db.session.query(Cafe).all()
        cafe_dict = [cafes[i].to_dict() for i in range(8, len(cafes))]
        print(cafe_dict)
        return jsonify(cafes=cafe_dict)

    @app.route('/search', methods=['GET'])
    def search():
        query_location = request.args.get('loc')
        cafe = db.session.query(Cafe).filter_by(location=query_location).first()
        if cafe:
            return jsonify(cafe=cafe.to_dict())
        else:
            jsonify(error={"Not Found": "Sorry we don't have a cafe at that location."})



    ## HTTP POST - Create Record
    @app.route('/add',methods=['POST'])
    def add():
        new_cafe = Cafe(name=request.form.get("name"),
                        map_url=request.form.get("map_url"),
                        img_url=request.form.get("img_url"),
                        location=request.form.get("location"),
                        has_sockets=bool(request.form.get("sockets")),
                        has_toilet=bool(request.form.get("toilet")),
                        has_wifi=bool(request.form.get("wifi")),
                        can_take_calls=bool(request.form.get("calls")),
                        seats=request.form.get("seats"),
                        coffee_price=request.form.get("coffee_price")
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"Success": "Successfully added the new cafe."})

    ## HTTP PUT/PATCH - Update Record
    @app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
    def patch(cafe_id):
        new_price = request.args.get("new_price")
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            cafe.coffee_price = new_price
            db.session.commit()
            return jsonify(response={"Success": "Successfully updated coffee price."})
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


    ## HTTP DELETE - Delete Record

    @app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
    def delete_cafe(cafe_id):
        api_key = request.args.get("api-key")
        if api_key == "TopSecretAPIKey":
            cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
            if cafe:
                db.session.delete(cafe)
                db.session.commit()
                return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
            else:
                return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        else:
            return jsonify(
                error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403



    if __name__ == '__main__':
        app.run(debug=True)
