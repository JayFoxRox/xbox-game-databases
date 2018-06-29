Tools to fetch information about Xbox games from various databases

# xqemu-compatibility-inspector.py

**Note for Windows users**

For Windows, we have tested [MSYS2](http://www.msys2.org/).
After installing MSYS2 you need to run the following commands to install pip:

```
pacman -S python3-pip
pip3 install --upgrade pip
```

Then close your existing MSYS2 Shell and open a new one ("MSYS2 MSYS" in start menu).
Then run the instructions below.

## Instructions

These instructions should work for most platforms which have git and Python (including pip) installed:

```
git clone https://github.com/JayFoxRox/xbox-game-databases.git
cd xbox-game-databases
pip3 install colorama
pip3 install --upgrade google-api-python-client
python3 xqemu-compatibility-inspector.py
```

Then follow the onscreen directions to set up your [Google API key](https://goo.gl/3UN7Ut).


---

# List of useful resources

Some of these might not be implemented.

## Disc Integrity

http://redump.org/

## Disc Scans

http://www.covergalaxy.com/

## Covers

http://www.covergalaxy.com/
http://www.thecoverproject.net/

## Used engines

http://xboxdevwiki.net/Engine_List

## Emulator compatibility

http://xboxdevwiki.net/XQEMU/Compatibility_List

---

**© 2017 Jannik Vogel**

Licensed under GPL version 2 or later.
