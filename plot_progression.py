from learntrueskill import load_replays
import pytrueskill as ts
import numpy as np
import matplotlib.pyplot as plt
import csv
import scipy.stats

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

nPlayersExamine = 5
figs_progression = [ plt.subplots() for n in range(nPlayersExamine) ]
fig_filenames = { }
probabilities = [ [] for n in range(nPlayersExamine) ]
all_probabilities = []
aliases = [None for n in range(nPlayersExamine)]
environments = ( np.array([1500., 500., 250., 5., 0.1]),
                 np.array([1500., 500., 240., 10., 0.045]),
                 np.array([1500., 500., 240., 18., 0.045]) )

for nenv,env in enumerate(environments):

    ratings[:,0] = env[0]
    ratings[:,1] = env[1]
    r1,r2,nGames1,nGames2,L = ts.rate_1vs1(env,pids1,pids2,scores12,ratings)
    all_probabilities += [L]

    finalGameCount = np.zeros(nplayers,dtype=np.int)
    finalGameCount[pids1] = nGames1
    iSorNGames = np.argsort(finalGameCount)[::-1]
    for nplayer,((f1,ax1),PID) in enumerate(zip(figs_progression,iSorNGames)):
        idx1 = pids1==PID
        idx2 = pids2==PID
        aliases[nplayer] = ','.join(playerAliases[PID][1:])

        mu = idx1*r1[:,0] + idx2*r2[:,0]
        sigma = idx1*r1[:,1] + idx2*r2[:,1]
        mu = mu[idx1 | idx2]
        sigma = sigma[idx1 | idx2]
        l = L[idx1 | idx2]
        probabilities[nplayer] += [l]

        label = 'mu=%d, sigma=%d, beta=%d, tau=%.1f, pdraw=%.2f, L=%d' % tuple([x for x in env] + [np.sum(np.log(l))])
        ax1.plot(np.arange(len(mu)),mu-3*sigma,label=label)
        ax1.set_title(aliases[nplayer])
        ax1.legend(loc='lower center', prop={'size':8})
        ax1.grid(True)
        fig_filenames[f1] = 'rating_progression_%s.png' % (aliases[nplayer])

for f,ax in figs_progression:
    f.savefig(fig_filenames[f])
    plt.close(f)

for nplayer,(l,alias) in enumerate(zip(probabilities,aliases)):
    getlabel = lambda n: 'mu=%d, sigma=%d, beta=%d, tau=%.1f, pdraw=%.2f, L=%d' % tuple([x for x in environments[n]] + [np.sum(np.log(l[n]))])

    logL = np.array(l).T
    fig,ax = plt.subplots()
    for n in range(len(environments)):
        ax.plot(np.sort(logL[:,0]), np.sort(logL[:,n]), '-', linewidth=1, label=getlabel(n))
    ax.set_xlabel('quantile')
    ax.set_ylabel('quantile')
    ax.set_title('QQ plots, predicted probability of outcome, %s' % (alias))
    ax.legend(loc='lower right', prop={'size':8})

    fig.savefig('QQ_predicted_probability_of_outcome_%s.png' % (alias))
    plt.close(fig)

fig,ax = plt.subplots()
l = np.array(all_probabilities).T
logl = np.log(all_probabilities).T
labels = [ 'mu=%d, sigma=%d, beta=%d, tau=%.1f, pdraw=%.2f, L=%d' % tuple([x for x in env] + [np.sum(logl[:,n])]) for n,env in enumerate(environments) ]
for n,env in enumerate(environments):
    ax.plot(np.sort(l[:,0]), np.sort(l[:,n]), '-', linewidth=1, label=labels[n])
ax.set_xlabel('quantile')
ax.set_ylabel('quantile')
ax.set_title('QQ plots, predicted probability of outcome')
ax.legend(loc='lower right', prop={'size':8})
fig.savefig('QQ_predicted_probability_of_outcome.png')
plt.close(fig)

fig,ax = plt.subplots()
ax.hist(l,bins=100,histtype='step',label=labels)
ax.set_xlabel('predicted probability of outcome')
ax.set_ylabel('frequency')
ax.legend(loc='lower center',prop={'size':8})
fig.savefig('distribution_predicted_probability_of_outcome.png')
plt.close(fig)