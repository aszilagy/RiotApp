# List of things to do:
1. Add a page for configuring tournament settings (spectatorType, mapType, pickType)
2. Add summonerMastery API call (and add info to summoner Object)
  a. Add these stats to the table (rank, misc..)
  b. Add a menu to interact with summoner stats (detailedView)
3. Add Spectator API call (https://developer.riotgames.com/api-methods/#spectator-v4)
4. On *ChampSelectStartedEvent*, run Spectator API to monitor pre-game lobby
  a. This needs it's own UI and should be a seperate page?
5. Monitor in game stats on a live game via Match API (https://developer.riotgames.com/api-methods/#match-v4)
  a. This will need it's own UI/Page as well
