# Resource Pack Utils

Utilities to help deal with Minecraft's *the flattening*.

## Resources

Within this directory we store block/item and texture information.

### Files

*New refers to 1.13+, and old 1.12-*

Each file is named by of `newblockname.json`.

#### File format

```
{
  "type": "type",
  "game": {
    "old": {
      "id": 14,
      "damage": 2
    },
    "new": {
      "name": "block_name"
    }
  },
  "file": {
    "pre": "path/to/file",
    "post": "path/to/file"
  }
}
```

- `type` What type of texture this is. Different blocks consist of multiple textures. Allowed values: `single` `top` `bottom` `side` `end` `front`. These are based off of the block models. Single should be the most used. It's its only texture.' When in doubt, `single`.

- `game` consists of how the game views the item/block. If it didn't exist prior to 1.13 in `old` just put `null`. In `old` `id` is the ID that minecraft gives it (int), same with damage. For `new` block_name is its new namespace.

- `file` consists of where the default file is located. Don't include the base folder. (i.e let's say I have a texturepack called DefaultPlus, the blocks folder would be `assets/minecraft/textures/blocks`)