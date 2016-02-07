from replays import logger
from PyQt4 import QtCore
import json
import csv
from PlayerAliases import getPlayerOriginalName

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


class ReplayDumper:

    def __init__(self, replayswidget):

        logger.info('Creating replay dumper ...')
        self.replayswidget = replayswidget
        
        self.replays = { }
        self.replayPlayers = { }
        self.playerAliases = { }

        self.heartbeat = 20
        self.savecountdown = 300
        QtCore.QTimer.singleShot(1000, self.onHeartbeatTimer)

        self.requestDetails = set()
        self.requestReplaysByPlayer = set()
        self.alreadySearchedPlayers = set()
        

    def cachePlayerAlias(self,player):
        
        if player in self.playerAliases:
            return self.playerAliases[player]

        else:
            player0 = getPlayerOriginalName(player)
            self.playerAliases[player] = player0
            logger.info('Player %s known as %s' % (player, player0))
            return player0


    def resume(self):
        with open('d:/replaydumper.json') as fp:
            dump = json.load(fp)
            dump = byteify(dump)

        self.replays = { int(k):v for k,v in dump['replays'].iteritems() }
        self.replayPlayers = { int(k):v for k,v in dump['replayPlayers'].iteritems() }
        self.playerAliases = { } #dump['playerAliases']

        for replayid,players in self.replayPlayers.iteritems():
            for player in players:
                self.requestReplaysByPlayer.add(player['name'])

        logger.info('Resuming search: %d replays retrieved, %d player names to search' % (
            len(self.replays), len(self.requestReplaysByPlayer)
        ))
        self.pollRequests()
        
        
    def onHeartbeatTimer(self):

        self.heartbeat -= 1
        self.savecountdown -= 1

        # take this opportunity to save everything to disk
        if self.heartbeat < 0 or self.savecountdown < 0:
            self.savecountdown = 300
            logger.info('Saving replay dump ...')
            with open('d:/replaydumper.json','w') as fp:
                fp.write(json.dumps({
                    'replays':self.replays,
                    'replayPlayers':self.replayPlayers,
                    'playerAliases':self.playerAliases
                }))

        # detect and deal with a dead polling cycle
        if self.heartbeat < 0 and (self.requestDetails or self.requestReplaysByPlayer):
            logger.info('Dead poll loop. restarting')
            self.heartbeat = 20
            self.pollRequests()

        # keep going as long as the heart beat hasn't expired
        if self.heartbeat >= 0:
            QtCore.QTimer.singleShot(1000, self.onHeartbeatTimer)


    def pollRequests(self):

        while self.requestDetails:
            replayId = self.requestDetails.pop()
            if not replayId in self.replayPlayers:
                logger.info('Request info for replay %d (%d in queue) ...' % (replayId, len(self.requestDetails)))
                self.replayswidget.connectToModVault()
                self.replayswidget.send(dict(command="info_replay", uid=replayId))
                return

        while self.requestReplaysByPlayer:
            playerName = self.requestReplaysByPlayer.pop()
            playerName0 = self.cachePlayerAlias(playerName)

            if (playerName0 != playerName) and (playerName0 not in self.alreadySearchedPlayers):
                self.requestReplaysByPlayer.add(playerName0)
            
            if playerName not in self.alreadySearchedPlayers:
                logger.info('Request replays for player "%s" (%d in queue) ...' % (playerName, len(self.requestReplaysByPlayer)))
                self.replayswidget.connectToModVault()
                self.replayswidget.send(dict(
                    command="search",
                    rating=self.replayswidget.minRating.value(),
                    map=self.replayswidget.mapName.text(),
                    player=playerName,
                    mod=self.replayswidget.modList.currentText()
                ))
                self.alreadySearchedPlayers.add(playerName)
                return


    def onReplays(self, replays):
        self.heartbeat = 20
        allReplays = { replay['id']:replay for replay in replays }
        logger.info('Received %d replays' % len(allReplays))
        self.replays.update(allReplays)
        self.requestDetails.update(allReplays.keys())
        QtCore.QTimer.singleShot(10, self.pollRequests)


    def onInfoReplay(self, uid, players):
        self.heartbeat = 20
        self.replayPlayers[uid] = players
        
        for player in players:
            self.requestReplaysByPlayer.add(player['name'])

        QtCore.QTimer.singleShot(10, self.pollRequests)
