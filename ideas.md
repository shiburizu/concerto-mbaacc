* FTx challenges - client side implementation using the update_stats function
* Queue lobby - Generate a timestamp when a match up is created to send to the players to show a countdown using a thread.
* Allow netplay matchmaking to show player names in stats
* BattleLog viewer
* Frame data viewer
* Training script launcher

* re-implement wiki buttons on host's screen
* re-do the host/join/matchmaking functions to use regex everywhere

# v1.0.5
- Removed the How To Play guide, previously accessible from the Resources screen.
- Added a link to the MBAACC Help Portal (https://mbaacc.gitbook.io) in the Resources screen.
- While hosting a Direct Match session or standing by in Matchmaking, you can now launch training mode.
- Added UI for screen resolution choice and fullscreen/windowed mode toggle in the Options screen.
- Deprecated Windows 8.1 and prior. By leveraging backend features only in Windows 10 and above, it is expected the program will trigger less false positives in Windows Defender.
- Lobbies are now much more responsive by querying the server for information much more often.
- Added the Global Lobby button, a quick way to join a public lobby, to the Online screen.
- "Lobbies" have been re-named to "Player Rooms" to reflect the addition of a singular Lobby.
- Renamed "Quick Match" in the  Online screen to "Matchmaking".
- Re-factored UI code to enable translation of the interface.
- Re-factored interface with CCCaster to (hopefully) make interaction more reliable.
- Various bug fixes.