# Introduction

Simple script to plan trip in selected city and country. It is asking openAI for attactions based on <https://www.tripadvisor> and <https://www.thecrazytourist.com>.
You can select minimum and maximum number of attraction returned by OpenAI. Data is returned in HTML format. Lter it is parsed via Google Map API to KML file. The file might be imported to custom map. Content with attached KML file is stored in given section in OneNote as new page.

## Requirements

Script requires 3 system variables:

    - OPENAI_API_KEY - OpenAI API key
    - Google_API_Key - Google Map API key
    - OneNote_Section_Id - OneNote section Id to which add page

## Usage to find attractions, create Google Map and add page to OneNote

```python
  usage: trip.py [-h] [--min MIN] [--max MAX] [--country COUNTRY] [--home HOME] city

  Plan a trip for selected place in given country.

  positional arguments:
    city               a city for which to plan the trip

  optional arguments:
    -h, --help         show this help message and exit
    --min MIN          Minimum number of returned attractions, e.g. 10. Default 15
    --max MAX          Maximum number of returned attractions, e.g. 10. Default 20
    --country COUNTRY  Optional country. Default Spain
    --home HOME        Optional home city, it is used to find direction to selected city. Default Barcelona
  ```

## Usage to search transportation and hotels stays

```python
  py server.py
  * Running on http://127.0.0.1:5000
```

 Open above page in browser (yes, I know there should be some design involved ;) )
 Fill the form. Please remember to double check results.

## Configure websties use during seard

 Please update config-{country}.json file for selected country.

 Example for Spain (config-spain.json):

## Resources

 -Google Maps Api
 -OneNote Api (Microsoft Graph)
 -https://www.w3resource.com/javascript-exercises/event/javascript-event-handling-exercise-6.php for drag & drop
 -OpenAI API
 -https://airlabs.co/docs/flight -> possible API to use to find flights information


 