from flask import Flask,  render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import lob, time, os

lob.api_key = os.environ.get('lobkey')

app = Flask(__name__)

#initialize the db
db_name = 'addresses.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class Address(db.Model):
    __tablename__ = 'addresses'
    _id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String)
    name = db.Column(db.String)
    address1 = db.Column(db.String)
    address2 = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zip5 = db.Column(db.String)
    countrycode = db.Column(db.String)
    lob_id = db.Column(db.String)

    def __init__(self, desc, name, address1, address2, city, state, zip5, countrycode, lob_id):
        self.desc = desc
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip5 = zip5
        self.countrycode = countrycode
        self.lob_id = lob_id


def makeaddress(desc, name, address1, address2, city, state, zip5, countrycode):
    addressobject = lob.Address.create(
        description = desc,
        name = name,
        address_line1 = address1,
        address_line2 = address2,
        address_city = city,
        address_state = state,
        address_zip = zip5,
        address_country = countrycode )
    
    return(addressobject)

def address_id_finder(addressdesc):
    filtered_address = Address.query.filter_by(desc = addressdesc).first()
    return filtered_address.lob_id

def img_selector(img):
    if img == "Beach":
        return "https://s3-us-west-2.amazonaws.com/public.lob.com/assets/beach.jpg"
    else:
        return "https://s3-us-west-2.amazonaws.com/public.lob.com/assets/jungle.jpg"

@app.route("/", methods = ["GET"])
def home():
    return render_template("home.html")

@app.route("/addaddress", methods = ["POST", "GET"])
def addaddress():
    if request.method == "POST":

        desc = request.form["inputdesc"]
        name = request.form["inputname"]
        address1 = request.form["inputAddress1"]
        address2 = request.form["inputAddress2"]
        city = request.form["inputCity"]
        state = request.form["inputState"]
        zip5 = request.form["inputZip"]
        countrycode = request.form["inputCountry"]

        try: 
            lobaddress = makeaddress(desc, name, address1, address2, city, state, zip5, countrycode) 

            lob_desc = lobaddress.description
            lob_name = lobaddress.name
            lob_address1 = lobaddress.address_line1
            lob_address2 = lobaddress.address_line2
            lob_city = lobaddress.address_city
            lob_state = lobaddress.address_state
            lob_zip = lobaddress.address_zip
            lob_country = lobaddress.address_country
            lob_address_id = lobaddress.id

            record = Address(lob_desc, lob_name, lob_address1, lob_address2, lob_city, lob_state, lob_zip, lob_country, lob_address_id)
            # Flask-SQLAlchemy magic adds record to database
            db.session.add(record)
            db.session.commit()
            return redirect(url_for('address_book', e = None)) 

        except Exception as e:
            print(e)
            return render_template("address_form.html", e=e)

    else:
        e = None
        return render_template("address_form.html", e=e)

@app.route("/addressbook", methods = ["GET"])
def address_book():
    addresses = Address.query.filter(Address.address1 != None).all()
    return render_template("address_book.html", addresses = addresses)

@app.route("/postcard", methods = ["POST","GET"])
def postcard():

    addresses = Address.query.filter(Address.address1 != None).all()

    if request.method == "POST":    

        pscname = request.form["pscname"]
        font_size = request.form["font_size"]
        color = request.form["color"]
        psc_image = request.form["psc_image"]
        address = request.form["address"]

        to_address_id = address_id_finder(address)
        img_url = img_selector(psc_image)
        try:
            psc_object = lob.Postcard.create(
                to_address = {
                    to_address_id
                    },
                size = '6x11',
                front = 'tmpl_3063ee02c202aab',
                back = 'tmpl_3063ee02c202aab',
                merge_variables = {
                    'name': pscname,
                    'fontsize' : font_size,
                    'color' : color,
                    'img' : img_url
                }
                )

            time.sleep(10)
            
            front_thumbs = psc_object.thumbnails[0]["large"]
            back_thumbs = psc_object.thumbnails[1]["large"]

            return render_template("embedded_preview.html", front = front_thumbs, back = back_thumbs)

        except Exception as e:
            print(e)
            return render_template("postcard.html", addresses = addresses, e = e)

    else:
        return render_template("postcard.html", addresses = addresses, e = None)
    
@app.route("/postcardpreview", methods = ["GET"])
def preview():
    return render_template("embedded_preview.html")

if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    port = int(os.environ.get('PORT', 5000)) #Heroku deployment reqs adding this port var 
    app.run(debug = True, host = '0.0.0.0', port=port) 