# PubMed LLM Search Engine
## Software Required
1. Neo4J
2. Python
3. Node.js

## Setup
The longest process is building the database, so I would recommend starting that before
going through the other steps as they can be done synchronously.

### 1. Install Python Packages
As long as you are in the root directory of this project, you should be able to run the following command in
the terminal: ```pip install -r requirements.txt``` which will be all you need for the next step.

### 2. Setting Up Neo4J
I would recommend using [Neo4J Desktop](https://neo4j.com/) as it was by far the easiest way
to create a database for the purposes of this project. The current code assumes that your database
is set up to use a standard port configuration for neo4j. This is shown in the config.json.

Once you have a database built, check that your config will match your desired database setup.
Once that's true, then the `create_neo4j.py` file can be run to ingest pubmed24n0001.xml provided
you have added it to the repository. It can be found here: https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/

If you'd like to use another version of the Annual Baseline, you need to change the file name at line 67 in 
`create_neo4j.py`.

This part will need to run for quite a while as it builds all the many nodes and edges based on this data. My
current version required `2.38 GB` of space for the data to be stored.

### 3. Building the React App
So long as you have Node.js installed, the setup for this app will be easy. CD into the `PubMed Search Frontend`
directory. Run `npm install` to initialize the required node modules. To run the frontend service you must run
this command: ```npm run dev```.

### 4. Start the LLM Server
To start the python server, all you need to do is run ```server.py```. You will not be able to access any LLM services without
configuring the config.json file to ensure that it has the correct API endpoint and service for your solution. Additionally,
you'll need to ensure that your API key is correct for the service of your choice.

## That's It!
Yup, the instructions above should have left you with a functional site that lets you ask your LLM solution to quiz your
database for information related to your queries. All code in this repository is provided as-is. You're welcome to point out
errors as you see them, but given this project is exploratory responses may not be guaranteed.

Additionally, the project is licensed under the provisions of the [GNU 3.0](https://www.gnu.org/licenses/gpl-3.0.en.html) license.




## Data Source
This project's database is built using the XML for the most recent version of the 
PubMed Annual Baseline. https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/