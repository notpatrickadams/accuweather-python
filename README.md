# Accuweather Python
An Accuweather API wrapper written in Python.

This wrapper really only deals with the limited accounts, not the paid for features.

##Instructions:
1. Pass your Accuweather API key to the Weather object.
2. Call a function:
  ⋅⋅1. getTodayForecast
    - Args: Local Code
  ⋅⋅2. getFutureForecast
    - Free version only goes up to 5 days
    - Args: Local Code
  ⋅⋅3. getLocalCode
    - Gets a local code based on query
    - Args: Name/Query (Location name)
    
