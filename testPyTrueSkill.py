import pytrueskill as ts
import numpy as np

env = np.array([1500., 500., 200., 30., 0.05])
r1 = np.array([
    [1400., 50.],
    [1500., 50.],
    [1600., 50.]
    ])

r2 = np.array([
    [1500., 10.],
    [1500., 10.],
    [1500., 10.]
    ])

q = ts.quality_1vs1(env,r1,r2)

print q
