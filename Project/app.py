import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from googletrans import Translator

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
translator = Translator()


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


def perevod(city):
    return translator.translate(f'{city}').text


def celc(grad):
    return str(round(float(5 * (float(grad) - 32.0) / 9), 2))


def get_req(city):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'
    r = requests.get(url.format(city)).json()
    if r["cod"] == "404":
        return False
    return r


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_city = request.form.get('city')

        if new_city:
            new_city_obj = City(name=new_city)
            db.session.add(new_city_obj)
            db.session.commit()

    cities = City.query.all()

    new_cities = []
    for i in cities:
        if perevod(i.name) not in new_cities:
            new_cities.append(perevod(i.name))

    weather_data = []
    for city in new_cities:
        t = get_req(city)
        if t != False:
            weather = {
                'city': city,
                'temperature': celc(t['main']['temp']),
                'description': t['weather'][0]['description'],
                'icon': t['weather'][0]['icon'],
            }
            weather_data.append(weather)
        else:
            print(f"Города {city} нет")

    return render_template('weather.html', weather_data=weather_data)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')