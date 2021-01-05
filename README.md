# MinecraftUtils

A package of different helpful utilities for dealing with Minecraft.

## Resource Packs

For fun resource pack modification, recolorization, and other random resource pack do-dads all you need to do is follow the instructions.

### Conversion (WIP)
Minecraft changed a lot from 1.12 to 1.13. A big chunk of it was them moving away from block ID's. Now it's all namespaced. Minecraft has zero support for <1.12 resource packs to >1.13 resource packs. To help with this we have created the flattening to convert these resource packs back and forth,and provide other resources.

## Instructions

To run this you'll need Python 3.6 or greater. When you have that make sure you have pip installed and run:
```
pip install -r requirements.txt
```

If you're going to be messing around with resource packs, it's recommended to have Minecraft's default texturepack assets folder in `./assets/convert/`. (This is easily configurable, but it's nice to have files in an easy place.)

Now all you need to do is run `main.py` and it will prompt you with what you want to do.

```
python main.py
```
