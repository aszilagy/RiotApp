# List of things to do:
1. Add a page for configuring tournament settings (spectatorType, mapType, pickType)
2. Add a menu to interact with summoner stats (detailedView) once they are clicked on **IN-PROGRESS**
    * There is a BUG with the teamSwap (I think?). Upon refresh, someone swaps teams. 
    * This requiers the Champion status API (https://developer.riotgames.com/static-data.html)
3. Add Spectator API call (https://developer.riotgames.com/api-methods/#spectator-v4)
4. On *ChampSelectStartedEvent*, run Spectator API to monitor pre-game lobby
    * This needs it's own UI and should be a seperate page?
5. Monitor in game stats on a live game via Match API (https://developer.riotgames.com/api-methods/#match-v4)
    * This will need it's own UI/Page as well
6. Create **CLASSES** and make the code actually clean.. (also improve performance)
    * Currently looking at 5.6s load times (on initial checking. Cacheing might help? I think most issues are from API calls)
