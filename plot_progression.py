import csv
import numpy as np
import matplotlib.pyplot as plt

with open('data/learning_results/learntrueskill_progression.txt') as fp:
    csvreader = csv.reader(fp)
    header = next(csvreader)
    data = np.recfromcsv(fp,delimiter=',',names=header)

pid=8264
idx1 = data.pid1==pid
idx2 = data.pid2==pid

mu = idx1*data.mu1 + idx2*data.mu2
sigma = idx1*data.sigma1 + idx2*data.sigma2
mu = mu[idx1 | idx2]
sigma = sigma[idx1 | idx2]

fig,ax = plt.subplots()
ax.plot(
    np.arange(len(mu)),mu-3*sigma,'k.',
    np.arange(len(mu)),mu,'r.',
    np.arange(len(mu)),mu+3*sigma,'k.'
)

plt.show(fig)
