# kaoibhinn

Welcome to the github repository for Kaoibhinn. A musical act 🎶 by Aoibhinn Reddington and Kai Blumberg.

## Repository Structure

* [demos](demos) - Digital audio files of the act
* [docs](docs) - Documentation files
	* [effects.md](docs/effects.md) - Documentation about input effects used.
* [src](src) - Source code
	* [effects](src/effects) - Dependency files for input effects. 
	* [rpp](src/rpp) - Reaper project files

## DAW Setup 

### Download and install Reaper

Download and install relevant operating system build from [Reaper download page](https://www.reaper.fm/download.php). [Reaper](https://www.reaper.fm/) is a Digital Audio Workstation (DAW) with an unlimited evaluation license, and open source community contributions. 

### Handling Latency 

Latency is the delay experienced from signal processing and can make it difficult/impossible to play live. The following might help fix latency issues.

* On windows set ASIO drivers (see [How to Fix Latency in REAPER](https://www.youtube.com/watch?v=JovPorQzzFs))
* Possibly reduce `Media Buffer Size` to something like `200` ms in `Reaper Preferences > Audio > Buffering`. This helps reduce latency with live effect processing.
* Possibly set a manual buffer adjustment (e.g. `17` ms) in `Reaper Preferences > settings> audio > Recording`
* Possibly change the `Request block size` (e.g. `64` ms down from default of 512) in `Reaper Preferences > Audio > Device`.

Additional Useful resources:
* [Adjusting the Buffer or Block Size in REAPER](https://www.youtube.com/watch?v=303eDz-8SW0)
* [How to Fix Latency in REAPER](https://www.youtube.com/watch?v=JovPorQzzFs)
* [Direct Monitoring (Zero Latency) in REAPER](https://www.youtube.com/watch?v=5Y2xFmGkakw)

### Download plugins

**Install the following plugins:**
* `VST3: NeuralAmpModeler (Steven Atkinson)` from [here](https://github.com/sdatkinson/NeuralAmpModelerPlugin)
* `VST3: TDR Nova (Tokyo Dawn Labs)` from [here](https://www.tokyodawn.net/tdr-nova/)

Restart `Reaper` after installation. Neither `NeuralAmpModeler` nor `TDR Nova` require anything (like paying or making a username/password) to download. 