import configparser
import numpy as np

# Define the scaling factors and file names for each resolution
resolutions = {
    "1080p_wide": {
        "factor": 1,
        "width_new": 2560,
        "filename": "config/res/game_2560x1080.ini",
    },
    "1440p": {
        "factor": 4.0 / 3.0,
        "filename": "config/res/game_2560x1440.ini",
    },
    "1440p_wide": {
        "factor": 4.0 / 3.0,
        "width_new": 3440,
        "filename": "config/res/game_3440x1440.ini",
    },
    "1600p": {
        "factor": 40.0 / 27.0,
        "width_new": 2560,
        "filename": "config/res/game_2560x1600.ini",
    },
    "1600p_wide": {
        "factor": 40.0 / 27.0,
        "width_new": 3840,
        "filename": "config/res/game_3840x1600.ini",
    },
    "2160p": {
        "factor": 2.0,
        "filename": "config/res/game_3840x2160.ini",
    },
    "1440p_ultra_wide": {
        "factor": 4.0 / 3.0,
        "width_new": 5120,
        "black_bars": [400, -400],
        "filename": "config/res/game_5120x1440.ini",
    },
    "1080p_ultra_wide": {
        "factor": 1,
        "width_new": 3840,
        "black_bars": [300, -300],
        "filename": "config/res/game_3840x1080.ini",
    },
}


# Function to scale values
def scale_values(values, factor, width_org=None, width_new=None, black_bars=None):
    # If the value is a list of numbers separated by commas, scale each one
    if "," in values:
        num_values = np.array([int(x) for x in values.split(",")], dtype=int) * factor
        if width_org is not None and width_new is not None:
            is_right_side = num_values[0] > width_org / 2
            if is_right_side:
                num_values[0] += width_new - width_org
            if black_bars is not None:
                offset = black_bars[1] if is_right_side else black_bars[0]
                num_values[0] += offset
        return ",".join(map(str, num_values.astype(int)))
    else:
        # It's a single number, scale it, convert it to int, and then to string
        return str(int(int(values) * factor))


def main():
    # Initialize the configparser object
    config = configparser.ConfigParser()

    # Read the original ini file
    config.read("config/res/game_1920x1080.ini")

    # Iterate over the resolutions to create new files
    for key, value in resolutions.items():
        # Copy the original configuration
        new_config = configparser.ConfigParser()
        new_config.read_dict(config)

        # Iterate through the sections and options to update values
        for section in new_config.sections():
            for option in new_config[section]:
                if section != "colors":  # Skip the [colors] section
                    # Scale the values
                    if "width_new" in value and not option.startswith("rel_"):
                        width_org = int(value["factor"] * 1920)
                        black_bars = None if "black_bars" not in value else value["black_bars"]
                        new_config[section][option] = scale_values(
                            new_config[section][option], value["factor"], width_org, value["width_new"], black_bars
                        )
                    else:
                        new_config[section][option] = scale_values(new_config[section][option], value["factor"])

        # Write the new configuration to a file
        with open(value["filename"], "w") as configfile:
            new_config.write(configfile, space_around_delimiters=False)


if __name__ == "__main__":
    main()
