# ![logo](assets/logo.png)

Filter items and sigils in your inventory based on affixes, aspects and thresholds of their values. For questions,
feature request or issue reports join the [discord](https://discord.gg/YyzaPhAN6T) or use github issues.

![sample](assets/thumbnail.jpg)]

## Features

- Filter items in inventory and stash
- Filter by item type and item power
- Filter by affix and their values
- Filter by aspects and their values
- Filter uniques by their affix and aspect values
- Filter sigils by blacklisting and whitelisting locations and affixes
- Supported resolutions: 1080p, 1440p, 1600p, 2160p - others might work as well, but untested

## How to Setup

### Game Settings

- Font size can be small or medium (better tested on small) in the Gameplay Settings
- Game Language must be English

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
- The advanced item comparison feature might cause incorrect classifications

### Configs

The config folder contains:

- __profiles/*.yaml__: These files determine what should be filtered
- __params.ini__: Different hotkey settings and number of chest stashes that should be looked at

### params.ini

| [general]                  | Description                                                                                                                                                                                  |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| profiles                   | A set of profiles seperated by comma. d4lf will look for these yaml files in config/profiles and in C:/Users/WINDOWS_USER/.d4lf/profiles                                                     |
| run_vision_mode_on_startup | If the vision mode should automatically start when starting d4lf. Otherwise has to be started manually with the vision button or the hotkey                                                  |
| check_chest_tabs           | Which chest tabs will be checked and filtered for items in case chest is open when starting the filter. Counting is done left to right. E.g. 1,2,4 will check tab 1, tab 2, tab 4            |
| hidden_transparency        | The overlay will become transparent after not hovering it for a while. This can be changed by specifying any value between [0, 1] with 0 being completely invisible and 1 completely visible |
| local_prefs_path           | In case your prefs file is not found in the Documents there will be a warning about it. You can remove this warning by providing the correct path to your LocalPrefs.txt file                |

| [char]    | Description                       |
|-----------|-----------------------------------|
| inventory | Your hotkey for opening inventory |

| [advanced_options] | Description                                                                                                              |
|--------------------|--------------------------------------------------------------------------------------------------------------------------|
| run_scripts        | Hotkey to start/stop vision mode                                                                                         |
| run_filter         | Hotkey to start/stop filtering items                                                                                     |
| exit_key           | Hotkey to exit d4lf.exe                                                                                                  |
| log_level          | Logging level. Can be any of [debug, info, warning, error, critical]                                                     |
| scripts            | Running different scripts                                                                                                |
| process_name       | Process name of the D4 app. Defaults to "Diablo IV.exe". In case of using some remote play this might need to be adapted |

## How to filter / Profiles

All profiles define whitelist filters. If no filter included in your profiles matches the item, it will be discarded.

Your config files will be validated on startup and will prevent the program from starting if the structure or syntax is
incorrect. The error message will provide hints about the specific problem.

The following sections will explain each type of filter that you can specify in your profiles. How you define them in
your YAML files is up to you; you can put all of these into just one file or have a dedicated file for each type of
filter, or even split the same type of filter over multiple files. Ultimately, all profiles specified in
your `params.ini` will be used to determine if an item should be kept. If one of the profiles wants to keep the item, it
will be kept regardless of the other profiles.

### Aspects

Aspects are defined by the top-level key `Aspects`. It contains a list of aspects that you want to filter for. If no
Aspect filter is provided, all legendary items will be kept. You have two choices on how to specify an item:

- You can use the shorthand and just specify the aspect name
- For more sophisticated filtering, you can use the following syntax: `[ASPECT_NAME, THRESHOLD, CONDITION]`. The
  condition can be any of `[larger, smaller]` and defaults to `larger` if no value is given. "Smaller" must be used
  when the aspect goes from a high value to a lower value (e.g., `Blood-bathed` Aspect)

<details><summary>Config Examples</summary>

```yaml
Aspects:
  # Filter for any umbral
  - of_the_umbral
  # Filter for a perfect umbral
  - [ of_the_umbral, 4 ]
  # Filter for all but perfect umbral
  - [ of_the_umbral, 3.5, smaller ]
```

</details>

Aspect names are lower case and spaces are replaced by underscore. You can find the full list of names
in [assets/lang/enUS/aspect.json](assets/lang/enUS/aspects.json).

### Affixes

Affixes are defined by the top-level key `Affixes`. It contains a list of filters that you want to apply. Each filter
has a name and can filter for any combination of the following:

- `itemType`: Either the name of THE type or a list of multiple types.
  See [assets/lang/enUS/item_types.json](assets/lang/enUS/item_types.json)
- `minPower`: Minimum item power
- `affixPool`: A list of multiple different rulesets to filter for. Each ruleset must be fulfilled or the item is
  discarded
    - `count`: Define a list of affixes (same syntax as for [Aspects](#Aspects)) and optionally `minCount`
      and `maxCount`. `minCount` specifies the minimum number of affixes that must match the item, `maxCount` the
      maximum number. If neither `minCount` nor `maxCount` is provided, all defined affixes must match
- `inherentPool`: The same rules as for `affixPool` apply, but this is evaluated against the inherent affixes of the
  item

<details><summary>Config Examples</summary>

```yaml
Affixes:
  # Search for chest armor and pants that are at least item level 725 and have at least 3 affixes of the affixPool
  - NiceArmor:
      itemType: [ chest armor, pants ]
      minPower: 725
      affixPool:
        - count:
            - [ damage_reduction_from_close_enemies, 10 ]
            - [ damage_reduction_from_distant_enemies, 12 ]
            - [ damage_reduction, 5 ]
            - [ total_armor, 9 ]
            - [ maximum_life, 700 ]
          minCount: 3

  # Search for boots that have at least 2 of the specified affixes and
  # either max evade charges or reduced evade cooldown as inherent affix
  - GreatBoots:
      itemType: boots
      minPower: 800
      inherentPool:
        - count:
            - maximum_evade_charges
            - attacks_reduce_evades_cooldown
          minCount: 1
      affixPool:
        - count:
            - [ movement_speed, 16 ]
            - [ cold_resistance ]
            - [ lightning_resistance ]
          minCount: 2

  # Search for boots with movement speed and 2 resistances from a pool of shadow, cold, lightning res
  - ResBoots:
      itemType: boots
      minPower: 800
      affixPool:
        - count:
            - [ movement_speed, 16 ]
        - count:
            - [ shadow_resistance ]
            - [ cold_resistance ]
            - [ lightning_resistance ]
          minCount: 2

```

</details>

Affix names are lower case and spaces are replaced by underscore. You can find the full list of names
in [assets/lang/enUS/affixes.json](assets/lang/enUS/affixes.json).

### Sigils

Sigils are defined by the top-level key `Sigils`. It contains a list of affix or location names that you want to filter
for. If no Sigil filter is provided, all Sigils will be kept.

<details><summary>Config Examples</summary>

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

If you want to filter for a specific affix or location, you can also use the `whitelist` key. Even if `whitelist` is
present, `blacklist` will be used to discard sigils that match any of the blacklisted affixes or locations.

```yaml
# Only keep sigils for vault_of_the_forsaken without any of the affixes armor_breakers and resistance_breakers
Sigils:
  minTier: 40
  maxTier: 100
  blacklist:
    - armor_breakers
    - resistance_breakers
  whitelist:
    - vault_of_the_forsaken
```

</details>

Sigil affixes and location names are lower case and spaces are replaced by underscore. You can find the full list of
names in [assets/lang/enUS/sigils.json](assets/lang/enUS/sigils.json).

### Uniques

Uniques are defined by the top-level key `Uniques`. It contains a list of parameters that you want to filter for. If no
Unique filter is provided, all unique items will be kept.
Uniques can be filtered similar to [Affixes](#Affixes) and [Aspects](#Aspects), but due to their nature of fixed
effects, you only have to specify the thresholds that you want to apply.

<details><summary>Config Examples</summary>

```yaml
# Take all uniques with item power > 800 
Uniques:
  - minPower: 900
```

```yaml
# Take all unique pants 
Uniques:
  - itemType: pants
```

```yaml
# Take all unique chest armors and pants
Uniques:
  - itemType: [ chest armor, pants ]
```

```yaml
# Take all unique chest armors and pants with min item power > 900
Uniques:
  - itemType: [ chest armor, pants ]
    minPower: 900
```

```yaml
# Take all Tibault's Will pants 
Uniques:
  - aspect: [ tibaults_will ]
```

```yaml
# Take all Tibault's Will pants that have item power > 900 and dmg reduction from close > 12 as well as aspect value > 25
Uniques:
  - aspect: [ tibaults_will, 25 ]
    minPower: 900
    affixPool:
      - [ damage_reduction_from_close_enemies, 12 ]
```

</details>

Unique names are lower case and spaces are replaced by underscore. You can find the full list of names
in [assets/lang/enUS/uniques.json](assets/lang/enUS/uniques.json).

## Custom configs

D4LF will search for `params.ini` and for `profiles/*.yaml` in `C:/Users/WINDOWS_USER/.d4lf`. All values
in `C:/Users/WINDOWS_USER/.d4lf/params.ini` will overwrite the values from the `params.ini` file in the D4LF folder. In
the profiles folder, additional custom profiles can be added and used.

This setup is helpful to facilitate updating to a new version as you don't need to copy around your config and profiles.

**In the event of breaking changes to the configuration, there will be a major release, such as updating from 2.x.x to
3.x.x.**

## Develop

### Python Setup

- Install [miniconda](https://docs.conda.io/projects/miniconda/en/latest/)

```bash
git clone https://github.com/aeon0/d4lf
cd d4lf
conda env create -f environment.yml
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
