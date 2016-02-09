from learntrueskill import load_replays
import pytrueskill as ts
import numpy as np
import matplotlib.pyplot as plt
import csv

replays = load_replays('data/replaydumper/replays.csv')
nplayers = 1 + max(np.max(replays.playerid1), np.max(replays.playerid2))
pids1 = replays.playerid1.astype(np.int)
pids2 = replays.playerid2.astype(np.int)
scores12 = (replays.score1 - replays.score2).astype(np.int)
ratings = np.empty((nplayers,2),dtype=np.float)

playerAliases = { }
with open('data/replaydumper/uniquePlayerIds.csv') as fp:
    csvreader = csv.reader(fp)
    for row in csvreader:
        playerAliases[int(row[0])] = row


figs = [ plt.subplots() for n in range(5) ]
fig_filenames = {  }
for env in ( np.array([1500., 500., 240., 18., 0.045]),
             np.array([1500., 500., 240., 10., 0.045]),
             np.array([1500., 500., 250., 5., 0.1]) ):

    ratings[:,0] = env[0]
    ratings[:,1] = env[1]
    r1,r2,nGames1,nGames2,L = ts.rate_1vs1(env,pids1,pids2,scores12,ratings)

    finalGameCount = np.zeros(nplayers,dtype=np.int)
    finalGameCount[pids1] = nGames1
    iSorNGames = np.argsort(finalGameCount)[::-1]
    for (f,ax),PID in zip(figs,iSorNGames):
        idx1 = pids1==PID
        idx2 = pids2==PID
        alias = ','.join(playerAliases[PID][1:])

        mu = idx1*r1[:,0] + idx2*r2[:,0]
        sigma = idx1*r1[:,1] + idx2*r2[:,1]
        mu = mu[idx1 | idx2]
        sigma = sigma[idx1 | idx2]
        l = L[idx1 | idx2]

        ax.plot(np.arange(len(mu)),mu-3*sigma,label='mu=%d, sigma=%d, beta=%d, tau=%.1f, pdraw=%.2f, L=%d' % tuple([x for x in env] + [np.sum(np.log(l))]))
        ax.set_title(alias)
        ax.legend(loc='lower center')
        ax.grid(True)
        fig_filenames[f] = 'rating_progression_%s.png' % (alias)

for f,ax in figs:
    f.savefig(fig_filenames[f])
    plt.close(f)
