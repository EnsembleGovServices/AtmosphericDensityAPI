# Atmospheric Density API

## About this API

Ensemble’s Atmospheric Density API delivers data files representing a continuously updated nowcast of Earth’s total atmospheric density, generating a nowcast file every 10 minutes.

* The API generates total atmospheric density in kg/m^3 as a function of longitude, latitude and partial pressure (instead of altitude). 
* The API is designed to easily facilitate satellite trajectory model flythroughs as a near real time solution to calculate the local ionospheric drag of satellites in LEO and MEO. 
* The model runs about 20 minutes ahead of real-time and nowcast files become accessible every 10 minutes. 
* The API provides model density on a geographic longitude, latitude, altitude grid in a series of timestamped parquet files 
    * Example output grid: (rho(lon, lat, alt)
    * The filename includes the date and time in ISO format.
* The API uses NOAA’s Coupled Thermosphere Ionosphere Plasmasphere Electrodynamics Model (CTIPe) currently hosted on the Integrated Space Weather Framework (ISWA) within the **Architecture for Collaborative Evaluation (ACE) compute** environment
* The API retains the previous 5 days worth of data, but will automatically delete data files after that time frame

The API converts raw model output to partial pressure using [Kamodo’s function composition and coordinate transformation space physics-as-a-service Analysis Suite.](https://ccmc.gsfc.nasa.gov/Kamodo/)


## Authentication

To use the endpoint you need to authenticate your self via passing the api-key in header showing below. To get the api-key mail us at [**ogerland@ensembleconsultancy.com**](mailto:ogerland@ensembleconsultancy.com).

## Data Access

### Base Endpoint

    https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1

### List Files

Endpoint: `/{bucket}`

Request Methods: `GET`

Headers: `"X-API-Key"` : `API_KEYS`

Example **URL**:
    
    https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data

Example **Response**: 
```yaml
{
    "start": 1,
    "limit": 100,
    "count": 870,
    "previous": "",
    "next": "?start=101&limit=100",
    "data": [
        "CTIPE_RHO_GEO_2022-08-18T07:20:00.parquet",
        "CTIPE_RHO_GEO_2022-08-18T07:10:00.parquet",
        "CTIPE_RHO_GEO_2022-08-18T07:00:00.parquet",
        "CTIPE_RHO_GEO_2022-08-18T06:50:00.parquet",
        "CTIPE_RHO_GEO_2022-08-18T06:40:00.parquet",
        "CTIPE_RHO_GEO_2022-08-18T06:30:00.parquet",
                            .
                            .
                            .
        "CTIPE_RHO_GEO_2022-08-17T15:20:00.parquet",
        "CTIPE_RHO_GEO_2022-08-17T15:10:00.parquet",
        "CTIPE_RHO_GEO_2022-08-17T15:00:00.parquet",
        "CTIPE_RHO_GEO_2022-08-17T14:50:00.parquet"
    ]
}
```


- Pass **next** or **previous** in the query to see the next files lists 

Example:

     https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data?start=11&limit=10


```python
import requests

headers = {'X-API-Key': 'API_KEY_HERE'}

request_url = 'https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data'

response = requests.get(request_url, headers=headers)

print(response.json())
```



### Download Files 

Endpoint: `/{bucket}/{file}`

Request Methods: `GET`

Headers: `"X-API-Key"` : `API_KEYS`


Example **URL**: 

    https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data/CTIPE_RHO_GEO_2022-05-13T00:10:00.parquet

Example **Response**:  This will download the file

```python
import requests

headers = {'X-API-Key': 'API_KEY_HERE'}

request_url = 'https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data/CTIPE_RHO_GEO_2022-05-13T00:10:00.parquet'

response = requests.get(request_url, headers=headers)

with open('CTIPE_RHO_GEO_2022-05-13T00:10:00.parquet', 'wb') as file:
    file.write(response.content)
```

- This will download the file from **S3** and store it in your local.

## Model Citation

The API uses NOAA’s Coupled Thermosphere Ionosphere Plasmasphere Electrodynamics Model (CTIPe) currently hosted on the Integrated Space Weather Framework within the **Architecture for Collaborative Evaluation (ACE)** environment, a shared compute eco-system between the Community Coordinated Modeling Center (CCMC) at NASA and the Space Weather Prediction Testbed (SWPT) at NOAA.

[http://ccmc-swpc.s3-website-us-east-1.amazonaws.com/about.html](http://ccmc-swpc.s3-website-us-east-1.amazonaws.com/about.html)

### Model Approach

* The coupled thermosphere ionosphere plasmasphere electrodynamics (CTIPe) model is a non-linear, coupled thermosphere-ionosphere-plasmasphere physically based numerical code that includes a self-consistent electrodynamics scheme for the computation of dynamo electric fields. The model consists of four distinct components which run concurrently and are fully coupled. Included are a global thermosphere, a high-latitude ionosphere, a mid and low-latitude ionosphere/plasmasphere and an electrodynamical calculation of the global dynamo electric field. model has evolved from an integration of a neutral thermospheric code and a high- and mid-latitude ionospheric model.

### Model Inputs

* The magnetospheric input to the model is based on the statistical models of auroral precipitation and electric fields described by Fuller-Rowell and Evans (1987) and Weimer (2005), respectively. Both inputs are keyed to solar wind measurements from ACE and/or DICOVR.
* The lower boundary condition in CTIPe is based on a free run of the Whole Atmosphere Model (WAM). Ionization rates from the EUV flux are evaluated from reference spectra for high and low solar activity on the basis of the Atmospheric Explorer (AE) measurements. The tidal inputs at the lower boundary are based on results from the global-scale wave model (GSWM) Hagan et al., (1995; 1999). The inclusion of the tidal forcing at the lower boundary as opposed to a higher pressure level as was done in previous versions of the model is described by Mueller-Wodrag et al., (2001).
* The joule heating calculation at high latitudes includes the effects of small-scale fluctuations in the E-field. The amplitude and spatial distribution of applied fluctuations is based on Millstone Hill Incoherent Scatter Radar data Codrescu et al., (2000). The average field at each grid point follows the diurnal variation prescribed by the Weimer model, while the small scale fluctuations are updated every minute. This procedure improves the neutral temperature structure as compared with MSIS.

### Model Developers

* Mihail Codrescu
* Tim Fuller-Rowell
* Mariangel Fedrizzi
* Catalin Neagrea
* Tomoko Matsuo
* Naomi Maruyama
* George Millward
