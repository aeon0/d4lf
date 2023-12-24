# ![logo](assets/logo.png)

Filter items and sigils in your inventory based on affixes, aspects and thresholds of their values. For questions, feature request or issue reports join the [discord](https://discord.gg/YyzaPhAN6T) or use github issues.

[![Alt text for thumbnail](assets/thumbnail.jpg)](https://www.youtube.com/watch?v=Paorfwl3GCg)

## Features
- Filter items in inventory and stash
- Filter by item type and item power
- Filter by affix and their values
- Filter by aspects and their values
- Filter uniques and their affix and aspect values
- Filter sigils by blacklisting locations and affixes
- Supported resolutions: 1920x1080, 3840x1080, 2560x1080, 2560x1440, 3440x1440, 5120x1440, 3840x2160

## How to Setup

### Game Settings
- Font size can be small or medium (better tested on small) in the Gameplay Settings
- Game Language must be English
- Advanced Tooltip Information (showing min and max values) is fine. But the __Advanced Tooltip Compare has to be truned off__!

### Run
- Download the latest version (.zip) from the releases: https://github.com/aeon0/d4lf/releases
- Execute d4lf.exe and go to your D4 screen
- There is a small overlay on the center bottom with buttons:
  - max/min: Show or hide the console output
  - filter: Auto filter inventory and stash if open (number of stash tabs configurable)
  - vision: Turn vision mode (overlay) on/off
- Alternative use the hotkeys. e.g. f11 for filtering


### Limitations
- The tool does not play well with HDR as it makes everything super bright

### Configs
The config folder contains:
- __profiles/*.yaml__: These files determine what should be filtered.
- __params.ini__: Different hotkey settings and number of chest stashes that should be looked at.
- __game.ini__: Settings regarding color thresholds and image positions. You dont need to touch this.

### params.ini
| [general] | Description |
| ----------------------- | --------------------------------------|
| profiles | A set of profiles seperated by comma. d4lf will look for these yaml files in config/profiles and in C:/Users/WINDOWS_USER/.d4lf/profiles. |
| run_vision_mode_on_startup | If the vision mode should automatically start when starting d4lf. Otherwise has to be started manually with the vision button or the hotkey. |
| check_chest_tabs | How many chest tabs will be checked and fitlered for items in case chest is open when starting the filter. E.g. 2 will check first two chest tabs |
| hidden_transparency | The overlay will go more transparent after not hovering it for a while. This can be any value between [0, 1] with 0 being completely invisible and 1 completely visible. Note the default "visible" transparancy is 0.89 |
| local_prefs_path | In case your prefs file is not found in the Documents there will be a warning about it. You can remove this warning by providing the correct path to your LocalPrefs.txt file |

| [char] | Description |
| ----------------------- | --------------------------------------|
| inventory | Hotkey for opening inventory |

| [advanced_options] | Description |
| ----------------------- | --------------------------------------|
| run_scripts | Hotkey to start/stop vision mode |
| run_filter | Hotkey to start/stop filtering items |
| exit_key | Hotkey to exit d4lf.exe |
| log_level | Logging level. Can be any of [debug, info, warning, error] |
| scripts | Running different scripts |

## How to filter

All items are whitelist filters. If a filter for an unique or a certain item type is not included in your .yaml filters, they will be discarded. All sigils are blacklist filted, meaning by default all sigils are good unless they match any of the blacklisted affixes. See more detailed descriptions below.

### Aspects
In your profile .yaml files any aspects can be added in the format of `[ASPECT_KEY, THRESHOLD, CONDITION]`. The condition can be any of `[larger, smaller]` and defaults to `larger` if no value is given. Smaller has to be used when the aspect go from high value to a lower value (eg. ‍Blood-bathed Aspect)

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
Affixes have the same structure of `[AFFIX_KEY, THRESHOLD, CONDITION]` as described above. Additionally, it can be filtered by `itemType`, `minPower` and `minAffixCount`. See the list of affix keys in [assets/affixes.json](assets/affixes.json). For items with inherent affixes `inherentPool` can be specified, then at least one of these has to match the inherent affixes on that item.

```yaml
Affixes:
  # Search for armor and pants that have at least 3 affixes of the affixPool
  - NiceArmor:
      itemType: [armor, pants]
      minPower: 725
      affixPool:
        - [damage_reduction_from_close_enemies, 10]
        - [damage_reduction_from_distant_enemies, 12]
        - [damage_reduction, 5]
        - [total_armor, 9]
        - [maximum_life, 700]
      minAffixCount: 3

  # Search for boots that have at least 2 of the specified affixes and
  # either max evade charges or reduced evade cooldown as inherent affix
  - GreatBoots:
      itemType: boots
      minPower: 800
      inherentPool:
        - maximum_evade_charges
        - attacks_reduce_evades_cooldown
      affixPool:
        - [movement_speed, 16]
        - [cold_resistance]
        - [lightning_resistance]
      minAffixCount: 2
```

### Uniques
Uniques are identified by their aspect (see [assets/aspects_unique.json](assets/aspects_unique.json)). They also have a affixPool, but since uniques have these fixed you only need to specify the ones you want to threshold.

```yaml
# Take all Tibault's Will pants that have item power > 900 and dmg reduction from close > 12 as well as aspect value > 25
Uniques:
  - aspect: [tibaults_will]
    minPower: 900
    affixPool:
      - [damage_reduction_from_close_enemies, 12]
```

### Sigils
Sigils are all ok unless they match any of the blacklisted locations or affixes. See all sigil locations and affixes here: [assets/sigils.json](assets/sigils.json)
```yaml
Sigils:
  minTier: 40
  maxTier: 100
  blacklist:
    # locations
    - endless_gates
    - vault_of_the_forsaken

    # affixes
    - armor_breakers
    - resistance_breakers
```

## Custom configs
D4LF will look for __params.ini__ and for __profiles/*.yaml__ also in C:/Users/WINDOWS_USER/.d4lf. All values in params.ini will overwrite the value from the param.ini in the D4LF folder. In the profiles folder additional custom profiles can be added and used.

This is helpful to make it easier to update to a new version as you dont need to copy around your config and profiles. In case there are breaking changes to the configuration there will be a major release. E.g. update from 2.x.x -> 3.x.x.

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
