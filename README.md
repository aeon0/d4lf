# ![logo](assets/logo.png)

Filter items in your inventory based on affixes, aspects and thresholds of their values. For questions, feature request or issue reports join the [discord](https://discord.gg/4rG6yD3dnD) or use github issues.

@Blizzard, please dont take this away from us. I can not bear to look at another affix...

[![Alt text for thumbnail](assets/thumbnail.jpg)](https://streamable.com/m84fnq)

## Features
- Filter items in inventory and if chest is open also in chest tabs (can be configured which ones)
- Filter by item type and item power
- Filter by affix and thresholds of their values
- Filter by aspects and threshold of their values
- Mark everything that does not pass the filter as junk
- Supported resolutions: 1080p, 1440p, 2160p

## How to Setup

### Game Settings
- Font size can be small or medium (better tested on small) in the Gameplay Settings
- Game Language must be English
- Advanced Tooltip Information (showing min and max values) is fine. But the Compare has to be truned off

### Run
- Download the latest version (.zip) from the releases: https://github.com/aeon0/d4lf/releases
- Execute d4lf.exe and go to your D4 screen
- There is a small overlay on the center bottom with buttons:
  - toggle: Make the console visiable or hide it
  - filter: Start filtering items
  - scripts: In case there are any scripts attached, run them
- Alternative use the hotkeys. e.g. f11 for filtering
- All items that do not match any of your filter configs will be marked as junk.

Note: Make sure to only have items in your inventory (will ignore junk and fav marked items). But elixirs (seen as magic) or material (seen as common) will be marked as junk!

### Configs
The config folder contains:
- __filter_aspects.yaml__: Filter settings for aspects.
- __filter_affixes.yaml__: Filter settings for affixes.
- __params.ini__: Different hotkey settings and number of chest stashes that should be looked at.
- __game.ini__: Settings regarding color thresholds and image positions. You dont need to touch this.

### params.ini
| [general] | Description |
| ----------------------- | --------------------------------------|
| check_chest_tabs | How many chest tabs will be checked and fitlered for items in case chest is open when starting the filter. E.g. 2 will check first two chest tabs |
| hidden_transparency | The overlay will go more transparent after not hovering it for a while. This can be any value between [0, 1] with 0 being completely invisible and 1 completely visible. Note the default "visible" transparancy is 0.89 |
| local_prefs_path | In case your prefs file is not found in the Documents there will be a warning about it. You can remove this warning by providing the correct path to your LocalPrefs.txt file |
| run_scripts | Running different scripts that can further help your gameplay |

| [char] | Description |
| ----------------------- | --------------------------------------|
| inventory | Hotkey for opening inventory |
| skill4 | Hotkey for casting the 4th skill in your skill bar. (Not needed for lootfilter!) |

| [advanced_options] | Description |
| ----------------------- | --------------------------------------|
| run_scripts | Hotkey to run scripts |
| run_filter | Hotkey to start/stop filtering items |
| exit_key | Hotkey to exit d4lf.exe |
| log_level | Logging level. Can be any of [debug, info, warning, error] |

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
