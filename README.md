# ![logo](assets/logo.png)

Filter items in your inventory based on affixes, aspects and thresholds of their values. For questions, feature request or issue reports join the [discord](https://discord.gg/4rG6yD3dnD) or use github issues.

@Blizzard, please dont take this away from us. I can not bear to look at another affix...

[![Alt text for thumbnail](assets/thumbnail.jpg)](https://streamable.com/2camxs)
## Getting Started

### Game Settings
- Supported resolutions: 1920x1080
- Font size must be set to small in the Gameplay Settings
- Game Language must be English
- You can keep the Advanced Tooltips turned on. But the "Compare" should not be active so your current items do not show up.

### Run
- Execute d4lf.exe. Diablo 4 must be running when starting to get the window resolution.
- When ingame and you want to filter items in your inventory. Press F11 to start the filter process. To stop immediately, press F12.
- All items that do not match any of your filter configs will be marked as junk

Note: If you get an error and it disappears very quickly, run the .exe in the command line.

Note2: If the item description doesnt show while hovering and is very laggy, try to move to another area without any events and less people around.

### Configs
The config folder contains:
- __filter_aspects.yaml__: Filter settings for aspects.
- __filter_affixes.yaml__: Filter settings for affixes.
- __params.ini__: Different hotkey settings. Mainly you want to adjust your hotkey to open the inventory.
- __game.ini__: Settings regarding color thresholds and image positions. You dont need to touch this.

## How to filter
### Aspects
In [config/filter_aspects.yaml](config/filter_aspects.yaml) any aspects can be added in the format of `[ASPECT_KEY, THRESHOLD, CONDITION]`. The condition can be any of `[larger, smaller]` and defaults to `larger` if no value is given.

For example:
```yaml
Aspects:
    # Filter for a perfect umbral
    - [aspect_of_the_umbral, 4]
    # Filter for any umbral
    - aspect_of_the_umbral
```
Aspect keys are lower case and spaces are replaced by underscore. You can find the full list of keys in [assets/aspect.json](assets/aspects.json). If Aspects is empty, all legendary items will be kept.

### Affixes
Affixes have the same structure of `[AFFIX_KEY, THRESHOLD, CONDITION]` as described above and are added to [config/filter_affixes.yaml](config/filter_affixes.yaml). Additionally, it can be filtered by `itemType`, `minPower` and `minAffixCount`. See the list of affix keys in [assets/affixes.json](assets/affixes.json). Uniques are by default always kept while Magic and Common items are discarded as junk by default.

```yaml
Filters:
  # Search for armor and pants that have at least 3 affixes of the affixPool
  - Armor:
      itemType: [armor, pants]
      minPower: 725
      affixPool:
        - [damage_reduction_from_close_enemies, 10]
        - [damage_reduction_from_distant_enemies, 12]
        - [damage_reduction, 5]
        - [total_armor, 9]
        - [maximum_life, 700]
      minAffixCount: 3
```

Note: If an itemType is not included in your filters, all items of this type will be discarded as junk! There is an example of a "TakeAll" filter in the filter_affixes.yaml. To keep an item type regardless of affixes and itemPower, add it there.

## Develop

### Python Setup
- Install [miniconda](https://docs.conda.io/projects/miniconda/en/latest/)
```bash
git clone https://github.com/aeon0/d4lf
cd d4lf
conda env create environment.yaml
conda activate d4lf
python src/main.py
```

### Linting
The CI will fail if the linter would change any files. You can run linting with:
```bash
conda activate d4lf
black .
```
To ignore certain code parts from formatting
```python
# fmt: off
# ...
# fmt: on

# fmt: skip
# ...
```
Setup VS Code by using the black formater extension. Also turn on "trim trailing whitespaces" is VS Code settings.

## Credits
- Icon based of: [CarbotAnimations](https://www.youtube.com/carbotanimations/about)
- Some of the OCR code is originally from [@gleed](https://github.com/aliig). Good guy.
- Names and textures for matching from [Blizzard](https://www.blizzard.com)
