FROM astropy/image-tests-py37-base:1.4

RUN apt-get update && apt-get install -y automake autogen build-essential make cmake gcc g++ libssl-dev
RUN pip3 install --user pkgconfig==1.5.1 Cython==0.29.21
RUN pip3 install --user pycapnp==1.1.0

RUN pip3 install cryptography

RUN apt-get install -y git

RUN git clone https://github.com/EnsembleGovServices/kamodo-core.git

RUN pip3 install -e kamodo-core

WORKDIR /kamodo-core

RUN pip3 install jupyter jupytext

RUN pip3 install fastparquet
RUN pip3 install ai.cs


CMD jupyter notebook /kamodo-core --port=8888 --no-browser --ip=0.0.0.0 --allow-root