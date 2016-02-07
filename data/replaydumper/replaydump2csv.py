import json
import numpy as np
import csv

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

with open('replaydumper.json') as fp:
    dump = json.load(fp)

dump = byteify(dump)

for k,v in dump.iteritems():
    for kk,vv in v.iteritems():
        print k, kk, vv
        break
print '-----'

# fudge missing entries in playerAliases
for id,players in dump['replayPlayers'].iteritems():
    for player in players:
        if player['name'] not in dump['playerAliases']:
            dump['playerAliases'][player['name']] = player['name']

# look for aliases that might need updating
andAgain = True
while andAgain:
    andAgain = False
    for oname in np.unique(dump['playerAliases'].values()):
        newName = dump['playerAliases'].get(oname,None)
        if (not newName is None) and newName != oname:
            andAgain = True
            print '%s better known as %s' % (oname, newName)
            dump['playerAliases'] = { k:v if v!=oname else newName for k,v in dump['playerAliases'].iteritems() }
            
# assign integer player ids
playerAliases = [ k for k,v in dump['playerAliases'].iteritems() ]
playerAliases_originalNames = [ v for k,v in dump['playerAliases'].iteritems() ]

uniqueOriginalNames, playerAliases_playerId = np.unique(playerAliases_originalNames, return_inverse=True)
with open('uniquePlayerIds.csv','w') as fp:
    csvwriter = csv.writer(fp)
    for pid,name in enumerate(uniqueOriginalNames):
        aliases = np.array(playerAliases)[playerAliases_playerId==pid]
        csvwriter.writerow([pid] + list(set([name]+list(aliases))))
playerAliasIds = { k:id for k,id in zip(playerAliases,playerAliases_playerId) }

# assign integer map ids
replayMaps = [ v['map'].split('.')[0] for k,v in dump['replays'].iteritems() ]
uniqueMapNames, replayMaps_mapId = np.unique(replayMaps, return_inverse=True)
with open('uniqueMapIds.csv','w') as fp:
    csvwriter = csv.writer(fp)
    for mapId,mapName in enumerate(uniqueMapNames):
        csvwriter.writerow([mapId,mapName])
replayMapIds = { k:id for k,id in zip(replayMaps,replayMaps_mapId) }

# dump to csv
with open('replays.csv','w') as fp:
    csvwriter = csv.writer(fp)
    header = ['replayid','mapid','start','end','duration','playerid1','faction1','color1','rating1','score1','place1','team1','playerid2','faction2','color2','rating2','score2','place2','team2']
    csvwriter.writerow(header)
    
    for replayId,replay in dump['replays'].iteritems():
        line = [ replayId, replayMapIds[replay['map'].split('.')[0]],
                 replay['start'], replay['end'] if replay['end']<4294967295 else np.nan, replay['duration'] if replay['end']<4294967295 else np.nan ]
        
        for player in dump['replayPlayers'].get(replayId,[]):
            line += [ playerAliasIds[player['name']], player['faction'], player['color'],
                      player.get('rating',np.nan), player.get('score',np.nan), player['place'], player['team'] ]

        line += [np.nan] * (len(header)-len(line))
        csvwriter.writerow(line)
