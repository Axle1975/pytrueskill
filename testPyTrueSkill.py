import pytrueskill as pyts
import trueskill as ts
import numpy as np
import time

def eval_pyts(env,pid1,pid2,scores):
    nplayers = 1+max(np.max(pid1),np.max(pid2))
    ratings = np.zeros((nplayers,2),dtype=np.float)
    ratings[:,0] = env[0]
    ratings[:,1] = env[1]
    return pyts.rate_1vs1(env,pid1,pid2,scores,ratings) + (ratings,)


def eval_tsorg(env,pid1,pid2,scores):
    nplayers = 1+max(np.max(pid1),np.max(pid2))
    ratings = np.zeros((nplayers,2),dtype=np.float)
    ratings[:,0] = env[0]
    ratings[:,1] = env[1]

    env = ts.TrueSkill(*list(env))
    r1_progression = np.zeros((len(pid1),2),dtype=np.float)
    r2_progression = np.zeros((len(pid2),2),dtype=np.float)
    
    for n in range(len(pid1)):
        r1 = env.create_rating(*list(ratings[pid1[n],:]))
        r2 = env.create_rating(*list(ratings[pid2[n],:]))

        r1_progression[n,:] = ratings[pid1[n],:]
        r2_progression[n,:] = ratings[pid2[n],:]

        if scores[n]>0:
            r1,r2 = env.rate_1vs1(r1,r2,drawn=False)
            
        elif scores[n]==0:
            r1,r2 = env.rate_1vs1(r1,r2,drawn=True)

        else:
            r2,r1 = env.rate_1vs1(r2,r1,drawn=False)

        ratings[pid1[n],0] = r1.mu
        ratings[pid1[n],1] = r1.sigma
        ratings[pid2[n],0] = r2.mu
        ratings[pid2[n],1] = r2.sigma


    return r1_progression,r2_progression,ratings
    

#env = np.array([25., 25./3., 25./6., 25./300., 0.1])
env = np.array([1500., 500., 250., 5., 0.1])
N = 1000
nPlayers = 5
pid1 = np.random.randint(0,nPlayers,N)
pid2 = np.random.randint(0,nPlayers,N)
idxClash = pid1==pid2
while np.any(idxClash):
    pid2[idxClash] = np.random.randint(0,nPlayers,np.sum(idxClash))
    idxClash = pid1==pid2
    
scores = 2*np.random.randint(0,2,N) -1
scores[np.random.randint(0,10,N)==0] = 0

t = [time.time()]
results_pyts = eval_pyts(env,pid1,pid2,scores)
t += [time.time()]
results_tsorg = eval_tsorg(env,pid1,pid2,scores)
t += [time.time()]
print 'pytrueskill(secs), trueskill.org(secs):', np.diff(t)

print '--- pytrueskill ---'
print 'final ratings:'
print results_pyts[-1]

print '--- trueskill.org ---'
print 'final ratings:'
print results_tsorg[-1]
