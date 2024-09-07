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
- COMPAS
- COMPAS FAB
- COMPAS RRC
- open3d
- numpy

## Installation
- COMPAS
- COMPAS FAB
- To build and test the project, follow the following steps:

### 1. Setting up the Anaconda environment with COMPAS, COMPAS_FAB AND COMPAS_RRC
```terminal
(base) conda config --add channels conda-forge
```
```terminal
(base) conda create -n undo compas_fab=0.27.0 --yes
```
```terminal
(base) conda activate undo
```
```terminal
(base) pip install compas-rrc
```
```terminal
(undo) python -m compas_rhino.install -v 7.0
```
