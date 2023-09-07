from flask import Flask, render_template, request
from country_list import countries_for_language

countries = dict(countries_for_language('en'))

app = Flask(__name__)

@app.route("/")
def start():
       return render_template('index.html', countries = countries)

@app.route("/planner", methods=['GET'])
def planner():
       print("Form was sent");
       args = request.args
       print(args)

       return render_template('planner.html')

if __name__ == "__main__":
    app.run()