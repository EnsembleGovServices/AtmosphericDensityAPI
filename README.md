
### About

### Setup

<!-- #region -->
Clone this repository into a working directory.

```sh
git clone https://github.com/EnsembleGovServices/AtmosphericDensityAPI.git
```

This directory contains:

* `CTIPE_DATA/` sample data files for CTIPe model
* `ctype/` python code for reading parquet files from `CTIPE_DATA` with Kamodo interface
* `WorkLog.md` a work log containing ongoing changes to code
* `Dockerfile` a docker image definition that includes all dependencies for reading and interpolating CTIPe
* `docker-compose.yaml` a docker environment to run the code and notebooks
<!-- #endregion -->

You will need to install docker for your platform to run the code as-is. Follow the install instructions for Docker here https://docs.docker.com/engine/install/


Once you have Docker installed, you should be able to start the notebook server from the root of this repo directory like this:

<!-- #region -->
```sh
cd AtmosphericDensityAPI # navigate into the cloned repo
docker compose up
```
<!-- #endregion -->

<!-- #region -->
This will build and start the notebook server at `localhost:8888`. In the console you'll see output that contains the jupyter server token similar to the following:

```sh
 docker compose up
Attaching to atmosphericdensityapi-ctipe-1
atmosphericdensityapi-ctipe-1  | [I 18:47:28.813 NotebookApp] Writing notebook server cookie secret to /root/.local/share/jupyter/runtime/notebook_cookie_secret
atmosphericdensityapi-ctipe-1  | [I 18:47:30.193 NotebookApp] [Jupytext Server Extension] Deriving a JupytextContentsManager from LargeFileManager
atmosphericdensityapi-ctipe-1  | [I 18:47:30.203 NotebookApp] Serving notebooks from local directory: /ctipe
atmosphericdensityapi-ctipe-1  | [I 18:47:30.203 NotebookApp] Jupyter Notebook 6.4.12 is running at:
atmosphericdensityapi-ctipe-1  | [I 18:47:30.203 NotebookApp] http://21df80d0353a:8888/?token=a5ea932fb36d507de48f43492843a42e6a575663fda9bdc4
atmosphericdensityapi-ctipe-1  | [I 18:47:30.203 NotebookApp]  or http://127.0.0.1:8888/?token=a5ea932fb36d507de48f43492843a42e6a575663fda9bdc4
atmosphericdensityapi-ctipe-1  | [I 18:47:30.203 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
atmosphericdensityapi-ctipe-1  | [C 18:47:30.220 NotebookApp] 

```
<!-- #endregion -->

Navigate to http://localhost:8888 and copy and paste the printed token (after the `?token=`) into the welcome screen. Click on `README.md` to open this file as a jupyter notebook. You should then be able to execute the following cells.


## Data retrieval

You may access the data from python using an API key provided by Ensmble LTD (email ogerland@ensembleconsultancy.com).

<!-- #region -->
Once received, save these credentials in a `.env` file colated with this repository and having the contents:

```bash
ENSEMBLE_API_ENDPOINT=https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data
ENSEMBLE_API_KEY=my_api_key # replace my_api_key with your API key
```
<!-- #endregion -->

If you used `docker compose up ctipe`, the above variables should be available to the container, which we can verify with the following code block:

```python
import os

assert 'ENSEMBLE_API_ENDPOINT' in os.environ #checking that api access info is present
assert 'ENSEMBLE_API_KEY' in os.environ
```

```python
import requests

headers = {'X-API-Key': os.environ['ENSEMBLE_API_KEY']}

request_url = os.environ['ENSEMBLE_API_ENDPOINT'] # https://32wm1ggs0a.execute-api.us-east-1.amazonaws.com/v1/ctipe-data

response = requests.get(request_url, headers=headers)
```

Now retrieve the most recent file name

```python
recent_fname = response.json()['data'][0]
recent_fname
```

Download the corresponding file

```python
import requests

headers = {'X-API-Key': os.environ['ENSEMBLE_API_KEY']}

request_url = f"{os.environ['ENSEMBLE_API_ENDPOINT']}/{recent_fname}"

response = requests.get(request_url, headers=headers)

with open(f"CTIPE_DATA/{recent_fname}", 'wb') as file:
    file.write(response.content)
```

The above file contains sample output from for a specific time and in geographic coordinates. Open the file with `fastparquet`, which comes preinstalled with this docker container.

```python
from fastparquet import ParquetFile

pf = ParquetFile(f"CTIPE_DATA/{recent_fname}")
df = pf.to_pandas()
```

```python
df.head()
```

The density data is stored in C-order with the last index (height) varying fastest. The grid is retrieved from the pandas multiindex.

```python
lon = df.index.levels[0].values
```

```python
lat = df.index.levels[1].values
```

```python
h = df.index.levels[2].values
```

```python
rho_data = df['rho[kg/m^3]'].fillna(0).values.reshape((len(lon), len(lat), len(h)))
```

## Interpolation


We'll interpolate the data in geographic coordinates using Scipy's [RegularGridInterpolator](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.RegularGridInterpolator.html). Note: This may introduce a small interpolation error due to curvature in the coordinate system.

```python
from scipy.interpolate import RegularGridInterpolator
```

```python
from kamodo import Kamodo, kamodofy

from kamodo import gridify

import numpy as np
```

```python
rgi = RegularGridInterpolator((lon, lat, h), rho_data, bounds_error = False, fill_value=0)

@kamodofy(units='kg/m^3')
@gridify(lon=lon, lat=lat, h=h, squeeze=True, order='C')
def rho_ijk(hvec):
    return rgi(hvec)

@kamodofy(units='kg/m^3')
def rho(hvec):
    return rgi(hvec)

k = Kamodo(rho=rho, rho_ijk=rho_ijk)

k
```

We've registered two versions of the density interpolator.
* $\rho(\vec{h})$ - A point interpolator taking a single (lon,lat,height) array of shape (n,3)
* $\rho_{ijk}(lon, lat, h)$ - A slice interpolating taking three arrays of varying shapes


The point interpolator is appropriate for large arrays of scattered positions, while the slice interpolator is more convenient for generating gridded positions. Under the hood, both functions invoke the same interpolating function.


The default values for the slice interpolator match the original data. This means a slice at fixed height will have the same resolution as the CTIPe grid:

```python
k.rho_ijk(h=h.mean()).shape
```

You can verify that the shape of the output matches the remaning position arrays:

```python
assert k.rho_ijk(h=h.mean()).shape == (len(lon), len(lat))
```

To plot the variables in 2-dimensions, we'll use kamodo's `partial` decorator to fix one of the axes.

```python
from kamodo import partial
```

```python
k['rho_lon'] = partial(k.rho_ijk, lon=50)
k.rho_lon
```

```python
k.plot('rho_lon')
```

Similarly, we can hold latitude constant:

```python
k['rho_lat'] = partial(k.rho_ijk, lat=0)
k.rho_lat
```

```python
k.plot('rho_lat')
```

Holding altitude constant:

```python
k['rho_h'] = partial(k.rho_ijk, h=h.mean())
k.rho_h
```

```python
k.plot('rho_h')
```

```python

```
