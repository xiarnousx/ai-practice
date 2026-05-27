from get_weather import get_weather

def kelvin2celsius(kelvin):
	return kelvin - 273.15

# Ask user for their desired location to lookup weather for
location = input("Enter a City Name: ")

# user the function in get_weather.py to get the weather for that location
# weather is returned in kelvin
weather = get_weather(location)

low_temp = kelvin2celsius(weather['main']['temp_min'])
high_temp = kelvin2celsius(weather['main']['temp_max'])

print(f"Low: {low_temp:.2f}°C, High: {high_temp:.2f}°C")
