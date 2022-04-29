# The Burrow: A Mini-Lob Clone

## Setup:

```bash
#install docker
$ brew cask install docker

#clone the repo locally
git clone https://github.com/mollukaren/python_burrow.git

# retrieve your Lob API key from the 'Settings' section of your Lob
# dashboard (requires a Lob account) and set it as an environment variable
# or wait for my demo, where I use my own test_key 

# build docker image from the python_burrow root
docker image build -t python_burrow .

# run the image, setting the environment variable using the -e tag as shown (port settings are flexible depending on your available ports):
docker run -e lobkey='${test_key_here}' -p 5000:5000 -d python_burrow

#if you prefer to avoid using env variables, you may directly set the
#api key in line 5 of flask_main.py
lob.api_key = "_your_key_here_"

# open the browser from the Docker GUI or by navigating to http://localhost:5000/ to launch the app

```

## Usage:

This webapp provides users access to two core Lob features:
	- Address Book functionality allowing users to save addresses
	- Postcard functionality allowing users to make and send dynamic postcards

### Navigation:
Outside of the home page, which exists only to introduce the app, there are 4 possible pages that users may access. 
- *Address Book* (/addressbook)
	- Accessed via nav-bar or URL
- *Add an Address* (/addaddress)
	- Accessed via clicking the 'Craw-ate an Address' button on Address Book or URL
- *Create a Postcrawd* (/postcard)
	- Accessed via nav-bar (Post Crawffice or URL
- *Postcard Preview* (/postcard#)
	- Accessed by submitting a valid request to create a postcard using the 'Craw-ate Postcard' button only
### Page Functionality & Data Entry
**Address Book:**
The *Address Book* is structured to present all user-uploaded addresses in a clear and easy to read format. When a user inputs address data, it is cleansed (using lob-api's *Address* endpoint), and the cleansed data is repopulated in the *Address Book* table.

**Add an Address:**
This page calls lob-api's *Address* endpoint to perform address validation and cleansing. 

To keep things reasonably constrained, this app has a structured form that only allows input of the following data when forming addresses:
- Address Label
- Name
- Address Line 1
- Address Line 2
- City
- State (from a drop down containing all 50 states)
- Zip
- Country (ISO 3166 codes only)

Any data issues get flagged by lob-api, from bad country codes and invalid ZIP's to incorrect API keys. When a failure occurs, a yellow error message will appear, and the user will stay on the address submission page, instead of being routed back to the Address Book.

In the database, address objects have an additional field called 'lob_id', which is populated by the lob-api endpoint upon address creation. This is referenced later when a postcard is made.

**Create a Postcrawd:**
This page calls lob-api's *Create Postcard* endpoint to perform Postcard creation and preview return. 

The postcard creation menu has similarly constrained data inputs, only allowing the following data:

- Postcard Addressee's Name
- Font
- Image
- Color
- Address (from a drop down containing all entries in a user's Address Book)

The request is formed by tapping an existing html template (tmpl_0fa67f8cc683dcb). To make this work for other accounts or for other templates, a code change on lines 134 and 135 is required.

A 10 second delay is expected between making a request and rendering the preview thumbnails because of some challenges I encountered with the async rendering processes on Lob's side. (Related note: the PM working on the rendering systems at Lob really needs to get his act together)

Error handling at this step in the processes is pretty opaque, but a future release would aim to fix this and allow more flexibility for template mapping, as opposed to the current app design referenced above. 

### Database FAQ
**Q.** What kind of db was used for this project?

**A.** This app uses a SQLite db


**Q.** What is the schema?

**A.** There is only one table, and the model is structured as follows:
```
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
```

**Q.** What functions make changes to the db and why?

**A.** Only the *Add Addresses* page makes changes to the db, since the only stored data are address objects. The *Address Book* and *Create a Postcrawd* pages  only read data from the db. 
 
	- Create : Add Addresses
	- Read : Address Book, Create a Postcrawd
	- Update : No way to update
	- Delete : No way to delete
