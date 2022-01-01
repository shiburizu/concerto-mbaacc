# <img src="res/concertoicon.png" width="40"> Concerto for MBAACC
* [**Project website**](https://concerto.shib.live)
* Development discussion & support at `#cc-modding` in [Melty Blood Community Server discord.](https://discord.gg/KeuSaJ5My8)

## About

Concerto is a graphical front end for CCCaster. This is a prototyping build used to test basic features for advanced implementation.

To use it, just drop `Concerto.exe` in the same folder as CCCaster. You need to be using the latest version of CCCaster and your caster executable needs to be named `cccaster.v3.1.exe` to work.

Other players can connect to your online versus host without Concerto as long as they use the same version of CCCaster.

For best usage don't open CCCaster or MBAA.exe on their own while using this program.

HIGHLY EXPERIMENTAL SOFTWARE, ENJOY AND EXPECT BUGS

## Building
This project requires Python version 3.8

### Install dependencies
```
pip install -r requirements.txt
```

### Building with Pyinstaller
```
pyinstaller concerto.spec
```
This will bundle the `Concerto.exe` executable into the `dist/` directory.

#### "winpty-agent.exe" is sourced from [winpty](https://github.com/rprichard/winpty) because we target [pywinpty](https://github.com/spyder-ide/pywinpty) version 0.5.7 for back compatibility to Windows 7 SP1. You may build and run Concerto using the latest version of pywinpty and exclude the .exe however the resulting build will only function on Windows 10.

## Customizing UI
It is possible to change the character art and background images by placing certain image file names in your MBAACC game directory.

* Each character art is the name of its respective screen: main.png, offline.png, online.png, resources.png
* Each background art is the name of its respective screen suffixed with _bg, i.e. main_bg.png
* The background art used for online lobbies, about, and How to Play screens is called lobby_bg.png

Each image is loaded directly onto the screen. For best results, make sure all images are 600x400px and keep in mind character arts are rendered above all other UI elements. See included files for examples.

## Audio/Visual sources
Art & sound are provided by community members for exclusive use with Concerto.
### Visuals
* [Arcuied by Bee Chan](https://twitter.com/Bee_Sempai/status/1345577709104205826?s=20)
* [Sion by aBitofbaileys](https://www.pixiv.net/en/artworks/90676177)
* [Riesbyfe by Onemi](https://www.pixiv.net/en/artworks/90219044)
* [Kohaku by Kohakudoori](https://www.pixiv.net/en/artworks/83141238)
* UI direction in cooperation with [okk](https://github.com/okkdev) and [M-AS](https://twitter.com/matthewrobo)
* Backgrounds sourced from Unsplash
### Audio
* "Soubrette's Walkway" by [Tempxa](https://twitter.com/TempxaRK9)
* "Fuzzy" by [softdrinks](https://twitter.com/soffdrinks)

## Development roadmap
This is a list of priorities attached to suspected version labels.

### Version 1.0 (first stable build)
* Lobby functions
* Mark player for spectating when match begins
* Direct online
* All offline functions
* Basic How to Play guide
* About & credits screens
* CCCaster & Concerto configuration screens
* Trial Mode
* Matchmaking

### Version 1.1 (First Major Update)
* JPN Localization
* Lobby tags, creation options, quick chat

### 2022 Projects
* EFZ Version

### Things to explore
* Frame data in-client
* Visual trial builder