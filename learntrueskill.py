import pytrueskill as ts
import numpy as np
import csv
import time

def load_replays(fn):
    
    with open(fn) as fp:
        csvreader = csv.reader(fp)
        header = next(csvreader)
        print header

        replays = np.recfromcsv(fp,delimiter=',',names=header)

    numPlayersInGame = (~np.isnan(replays.playerid1)).astype(np.int) + (~np.isnan(replays.playerid2)).astype(np.int)

    idxok = (numPlayersInGame == 2)
    idxok &= np.isfinite(replays.duration) & (replays.duration > 60)
    replays = replays[idxok]

    score1pos = np.isfinite(replays.score1) & (replays.score1>0)
    score1nan = np.isnan(replays.score1)
    score1neg = np.isfinite(replays.score1) & (replays.score1<0)
    score2pos = np.isfinite(replays.score2) & (replays.score2>0)
    score2nan = np.isnan(replays.score2)
    score2neg = np.isfinite(replays.score2) & (replays.score2<0)

    print 'outcome distribution'
    print np.array([ [ np.sum(u&v) for u in [score2neg, score2nan, score2pos] ] for v in [score1pos, score1nan, score1neg] ])
    print 'example replays per outcome'
    print np.array([ [ np.max(replays.replayid[u&v]) if np.sum(u&v)>0 else 0 for u in [score2neg, score2nan, score2pos] ] for v in [score1pos, score1nan, score1neg] ])

    idxok = ~(score1nan & score2nan)
    idxok &= ~(score1pos & score2pos)
    #idxok &= (~score1nan) & (~score2nan)
    replays = replays[idxok]

    isor = np.argsort(replays.replayid)
    replays = replays[isor]

    replays.score1[np.isnan(replays.score1)] = 0
    replays.score2[np.isnan(replays.score2)] = 0
    return replays


if __name__ == "__main__":
    replays = load_replays('data/replaydumper/replays.csv')
    nplayers = 1 + max(np.max(replays.playerid1), np.max(replays.playerid2))

    pids1 = replays.playerid1.astype(np.int)
    pids2 = replays.playerid2.astype(np.int)
    scores12 = (replays.score1 - replays.score2).astype(np.int)
    ratings = np.empty((nplayers,2),dtype=np.float)

    ub = np.array([1500., 600., 350., 30., 0.055])
    lb = np.array([1500., 400., 150., 10., 0.035])
    N=100000
    results = np.empty((N,6),dtype=np.double)
    for n in range(N):
        print n, '\r',
        env = np.random.uniform(0.,1.,5)
        env *= ub-lb
        env += lb
        ratings[:,0] = env[0]
        ratings[:,1] = env[1]
        r1,r2,nGames1,nGames2,L = ts.rate_1vs1(env,pids1,pids2,scores12,ratings)
        idx = (nGames1>10) & (nGames2>10)
        L = np.sum(np.log(L[idx]))
        results[n,0:-1] = env
        results[n,-1] = L

    idxOk = np.isfinite(results[:,-1])
    results = results[idxOk,:]
        
    isor = np.argsort(results[:,-1])
    results = results[isor,:]

    with open('learntrueskill_solution_space.txt','w') as fp:
        csvwriter = csv.writer(fp)
        csvwriter.writerow(['mu','sigma','beta','tau','pdraw','L'])
        csvwriter.writerows(results)

    env = results[-1,0:5]
    ratings[:,0] = env[0]
    ratings[:,1] = env[1]
    r1,r2,nGames1,nGames2,L = ts.rate_1vs1(env,pids1,pids2,scores12,ratings)

    with open('learntrueskill_progression.txt','w') as fp:
        csvwriter = csv.writer(fp)
        csvwriter.writerow(['pid1','mu1','sigma1','ngames1','pid2','mu2','sigma2','ngames2','scores12','L'])
        csvwriter.writerows(np.concatenate((
            pids1[:,np.newaxis],r1,nGames1[:,np.newaxis],pids2[:,np.newaxis],r2,nGames2[:,np.newaxis],scores12[:,np.newaxis],L[:,np.newaxis]
        ), axis=1))

    with open('learntrueskill_final_ratings.txt','w') as fp:
        csvwriter = csv.writer(fp)
        csvwriter.writerow(['pid','mu','sigma'])
        csvwriter.writerows(np.concatenate((
            np.arange(nplayers)[:,np.newaxis], ratings
        ), axis=1))
        
