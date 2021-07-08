# Concerto for MBAACC
* [**Project website**](https://concerto.shib.live)
* Development discussion & support at #modding in [Melty Blood Community Server discord.](https://discord.gg/KeuSaJ5My8)

## About

Concerto is a graphical front end for CCCaster. This is a prototyping build used to test basic features for advanced implementation.

To use it, just drop concerto.exe in the same folder as CCCaster. You need to be using the latest version of CCCaster and your caster EXE needs to be named "cccaster.v3.0.exe" to work.

Other players can connect to your online versus host without Concerto as long as they use the same version of CCCaster.

For best usage don't open CCCaster or MBAA.exe on their own while using this program.

HIGHLY EXPERIMENTAL SOFTWARE, ENJOY AND EXPECT BUGS

## Building
Requirements:
* kivy[base] - SDL2 is forced as audio provider to reduce bundle size.
* pywinpty==0.5.7*

.spec file provided for PyInstaller. 

* "winpty-agent.exe" is sourced from [winpty](https://github.com/rprichard/winpty) because we target [pywinpty](https://github.com/spyder-ide/pywinpty) version 0.5.7 for back compatibility to Windows 7 SP1. You may build and run Concerto using the latest version of pywinpty and exclude the .exe however the resulting build will only function on Windows 10.

## Audio/Visual sources
Art & sound are provided by community members for exclusive use with Concerto.
### Visuals
* [Arcuied by Bee Chan](https://twitter.com/Bee_Sempai/status/1345577709104205826?s=20)
* [Sion by aBitofbaileys](https://www.pixiv.net/en/artworks/90676177)
* [Riesbyfe by Onemi](https://www.pixiv.net/en/artworks/90219044)
* [Kohaku by Kohakudoori](https://www.pixiv.net/en/artworks/83141238)
* UI direction in cooperation with [Okk](https://github.com/okkdev) and [M-AS](https://twitter.com/matthewrobo)
* Backgrounds sourced from Unsplash
### Audio
* Main BGM (menu_bgm) by [Tempxa](https://twitter.com/TempxaRK9)
* Resources BGM (resource_bgm) by [softdrinks](https://twitter.com/soffdrinks)

## Development roadmap
This is a list of priorities attached to suspected version labels.

### Version 1.0 (first stable build)
* Lobby functions
* Direct online
* All offline functions
* Basic How to Play guide
* About & credits screens
* CCCaster & Concerto configuration screens

#### Todo for 1.0
* Broadcast game support DONE
* Fill out How to Play guide
* Rewrite server to be fast
* Mark player for spectating when match begins
* Player match details in lobby (character & moon)

### Version 1.1 (first major update)
* In-client game button binding
* Character introductions in Resources
* Results.csv viewer and analyzer

### Short-term goals
* Ping display in lobby
* Character/moon/win count display in lobby
* FTx challenges in lobbies (necessary for potential Ranked matchmaking)

### Long-term goals
* Matchmaking
* Support other Caster-based games (DFCI Transmission, EFZ Revival)

### Things to explore
* Frame data in-client
* Spectator mode (find random anon matches to watch)