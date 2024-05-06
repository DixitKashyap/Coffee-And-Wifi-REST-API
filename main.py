from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from random import choice
import json

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        #Method 1. 
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()



@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/random')
def random():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafe = result.scalars().all()
    random_cafe = choice(all_cafe)
    # return jsonify(cafe={
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price,
    # })
    return jsonify(random_cafe.to_dict())

@app.route('/all')
def get_all_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafe = result.scalars().all()
    json_list = []
    for cafe in all_cafe:
        json_list.append(cafe.to_dict())
    return jsonify(json_list)


@app.route('/search')
def get_cafe_loc():
    query = request.args.get('loc')
    print(query)
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query))
    all_cafe = result.scalars().all()
 
    if len(all_cafe) == 0:
        return jsonify({
            "error" :{
                "Not Found" : "Sorry we don't have any cafe at this location"
            }
        })
    else:
        json_list =[]
        for cafe in all_cafe:
            json_list.append(cafe.to_dict())

        return jsonify(json_list)    
    

    
# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})



# HTTP PUT/PATCH - Update Record
@app.route('/update-price/',methods=['PATCH'])
def patch_new_price():
    id = request.args.get('id')
    price = request.args.get("new_price")
    cafe = db.get_or_404(Cafe,id)
    if cafe:
        cafe.coffee_price = price
        db.session.commit()
        return jsonify({"Success " : "Successfully updated the price"}),200
    else :
        return jsonify({"Error " : "Not Found "}),404
    

# HTTP DELETE - Delete Record
@app.route('/delete',methods=["DELETE"])
def delete_Cafe():
    id = request.args.get('id')
    top_secret_key = request.args.get("api-key")
    if top_secret_key == 'TOPSECRETAPIKEY':
        cafe = db.get_or_404(Cafe,id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response = {"Success" : "Successfully delted the cafe"}),200
        else:
            return jsonify({"Error " : "Cafe not found"}),404
    else : 
        return jsonify({"Forbidden " : "Sorry ,that'not allowed "}) ,403   

if __name__ == '__main__':
    app.run(debug=True)
