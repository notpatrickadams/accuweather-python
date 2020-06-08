import requests, json
from datetime import datetime

class Weather:
    def __init__(self, key):
        self.apiKey = key
    def getLocalCode(self, name: str):
        """
        Gets the local code used for basically everything in this API.
        Uses the first result. If it doesn't match, be more specific (use the state or postal code)

        Keyword arguments:
        * name - The name of the city/town you want information for
        """
        r = requests.get(f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={self.apiKey}&q={name}").text

        return json.loads(r)[0]["Key"]

    def getPrecipitationInfo(self, obj, index):
        """
        Gets the precipitation information for the day. If there is any, get the rest of the information.
        """
        res = {}

        res.update({
            "precipitation bool day" : obj["DailyForecasts"][index]["Day"]["HasPrecipitation"], #true or false
            "precipitation bool night" : obj["DailyForecasts"][index]["Night"]["HasPrecipitation"], #true or false
        })

        if obj["DailyForecasts"][index]["Day"]["HasPrecipitation"] == True:
            res.update({
                "precipitation type day" : obj["DailyForecasts"][index]["Day"]["PrecipitationType"], #Type of precipitation (if any)
                "precipitation intensity day" : obj["DailyForecasts"][index]["Day"]["PrecipitationIntensity"] #How intense the precipitation is (if any)
            })
        if obj["DailyForecasts"][index]["Night"]["HasPrecipitation"] == True:
            res.update({
                "precipitation type night" : obj["DailyForecasts"][index]["Night"]["PrecipitationType"],
                "precipitation intensity night" : obj["DailyForecasts"][index]["Night"]["PrecipitationIntensity"]
            })
        return res

    def getTodayForecast(self, localcode: str):
        """
        Gets today's forecast for the town/city given.
        Returns a dictionary with normal info, then runs getPrecipitationInfo() and adds that to the dictionary being returned.

        Keyword arguments:
        * localcode - Code returned from Accuweather API or getLocalCode()
        """

        r = requests.get(f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{localcode}?apikey={self.apiKey}").text
        obj = json.loads(r)
        return dict({
            "commentary" : obj["Headline"]["Text"], #How the weather feels
            "temperature range" : [
                obj["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"], 
                obj["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
            ], #Min and max temperature in Fahrenheit
            "weather summary day" : obj["DailyForecasts"][0]["Day"]["IconPhrase"], #What the weather is going to look like today (example: mostly cloudy with thunderstorms)
            "weather summary night" : obj["DailyForecasts"][0]["Night"]["IconPhrase"],
        }, ** self.getPrecipitationInfo(obj, 0))

    def getFutureForecast(self, localcode: str, date: str):
        """
        Gets the weather forecast for a given day (within 5 days of whatever today is).

        Keyword arguments:
        * localcode - Code returned from Accuweather API or getLocalCode()
        * date - Date requested in format: %m-%d-%Y, (example: 06-06-2020 or 6-6-2020)
        """

        def checkDate(date: str, limit: int = 5):
            """
            Checks if the date provided is within the limit (default: 5)

            Keyword arguments:
            * date - Date requested in format: %m-%d-%Y, (example: 06-06-2020 or 6-6-2020)
            * limit - Number of days you want to check between today and the date given (default: 5)
            """
            delta = abs((datetime.today() - datetime.strptime(date, "%m-%d-%Y")).days)
            if delta > limit:
                return False
            return True

        if checkDate(date) == False:
            return {"Info" : "None"}

        queryDate = datetime.strptime(date, "%d-%m-%Y")
        index = 0

        r = requests.get(f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{localcode}?apikey={self.apiKey}").text
        obj = json.loads(r)
        for d in obj["DailyForecasts"]:
            parsedDate = d["Date"].split("T")[0]
            parsedDate = datetime.strptime(parsedDate, "%Y-%m-%d")
            if parsedDate == queryDate:
                index = d
        
        return dict({
            "date" : date,
            "temperature range" : [
                obj["DailyForecasts"][index]["Temperature"]["Minimum"]["Value"], 
                obj["DailyForecasts"][index]["Temperature"]["Maximum"]["Value"]
            ], #Min and max temperature in Fahrenheit
            "weather summary day" : obj["DailyForecasts"][index]["Day"]["IconPhrase"], #What the weather is going to look like today (example: mostly cloudy with thunderstorms)
            "weather summary night" : obj["DailyForecasts"][index]["Night"]["IconPhrase"],
        }, ** self.getPrecipitationInfo(obj, index))