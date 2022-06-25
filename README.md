# Soul Calibur 2 Plus ISO Builder

## Usage
### Requirements
 - Python 3.8 or later
 - Pip


### Building ISO
1. Clone repository and cd into folder.
```bash
cd sc2plus
```
2. Install required dependencies with pip.
```bash
pip install -r requirements.txt
```
3. [Download this mod zip file](https://www.mediafire.com/file/sza9ds77hzuhmme/mod-0.9.0.zip/file) and extract its contents to the mod folder.
4. Place a clean NTSC-U Soul Calibur 2 ISO in the base folder, rename it to grseaf.iso, and extract files.
```bash
python sc2plus.py -e
```
5. Expand extracted root.olk file.
```bash
python sc2plus.py -o
```
6. Add mod files to root.olk.
```bash
python sc2plus.py -p
```
7. Rebuild ISO.
```bash
python sc2plus.py -r
```

A Gamecube ISO named sc2plus.iso will be placed in the build folder