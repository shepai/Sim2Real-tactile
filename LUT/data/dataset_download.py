import opendatasets as od

dataset = 'https://www.kaggle.com/datasets/dextershepherd/optical-tactile-dataset-for-textures'
# Using opendatasets let's download the data sets
od.download(dataset)
dataset = 'https://www.kaggle.com/datasets/dextershepherd/texture-tactip'
# Using opendatasets let's download the data sets
od.download(dataset,username="dextershepherd",key="5eb76195c18fb253dbf59e5da0f3dc7a")

dataset = 'https://www.kaggle.com/datasets/dextershepherd/electrical-tactile-sensor'
# Using opendatasets let's download the data sets
od.download(dataset)