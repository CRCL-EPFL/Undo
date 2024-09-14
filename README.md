# Undo
UNDO ↺ Human-robot Interaction for Real-Time Design and Reconfiguration of Timber Structures

![UNDO_01](https://github.com/user-attachments/assets/f4e4f6f2-ed98-4e5e-bf9c-48d187bd0b3b)

# Getting Started
## Requirements
The project uses the following 3rd party libraries:
- Rhino 7 / Grasshopper
- Anaconda Python
- Visual Studio Code
- Github Desktop
- Docker Community Edition
- Agisoft Metashape 2.1.x

## Dependancies
- COMPAS==1.17.5
- COMPAS FAB==0.27.0
- COMPAS RRC
- open3d
- opencv
- numpy==2.0.0
- polyscope==2.2.1
- trimesh==4.4.3
- plyfile==1.0.3
- tabulate
- Metashape stand-alone Python module

## Installation

### 1. Setting up the Anaconda environment with COMPAS, COMPAS_FAB AND COMPAS_RRC
```terminal
(base) conda config --add channels conda-forge
```
```terminal
(base) conda create -n undo python=3.9
```
```terminal
(base) conda activate undo
```
```terminal
(undo) pip install compas_rrc=1.1.0
```
```terminal
(undo) pip install compas_fab=0.27.0
```
```terminal
(undo) python -m compas_rhino.install -v 7.0
```
### 2. Install undo library
```terminal
(undo) cd C:\Users\eleni\Documents\GitHub\Undo>
```
```terminal
(undo) C:\Users\eleni\Documents\GitHub\Undo> pip install -e.
```
### 3. Install Metashape module as a regular wheel package which you downloaded from [here](https://agisoft.freshdesk.com/support/solutions/articles/31000148930-how-to-install-metashape-stand-alone-python-module)
on Windows (64-bit)
```terminal
(undo) python3.exe -m pip install Metashape-2.1.2-cp37.cp38.cp39.cp310.cp311-none-win_amd64.whl
```
on mac
first, rename the wheel file you downloaded to the following: Metashape-2.1.3-cp37.cp38.cp39.cp310.cp311-abi3-macosx_11_0_universal2.macosx_10_13_x86_64.whl

```terminal
(undo) python3 -m pip install Metashape-2.1.3-cp37.cp38.cp39.cp310.cp311-abi3-macosx_11_0_universal2.macosx_10_13_x86_64.whl
```
