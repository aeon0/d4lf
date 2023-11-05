import configparser
import numpy as np

# Define the scaling factors and file names for each resolution
resolutions = {
    "1440p": {"factor": 4 / 3, "filename": "config/game_2560x1440.ini"},
    "2160p": {"factor": 2.0, "filename": "config/game_3840x2160.ini"},
}


# Function to scale values
def scale_values(values, factor):
    # If the value is a list of numbers separated by commas, scale each one
    if "," in values:
        num_values = np.array([int(x) for x in values.split(",")], dtype=int) * factor
        return ",".join(map(str, num_values.astype(int)))
    else:
        # It's a single number, scale it, convert it to int, and then to string
        return str(int(int(values) * factor))


def main():
    # Initialize the configparser object
    config = configparser.ConfigParser()

    # Read the original ini file
    config.read("config/game_1920x1080.ini")

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
                    new_config[section][option] = scale_values(new_config[section][option], value["factor"])

        # Write the new configuration to a file
        with open(value["filename"], "w") as configfile:
            new_config.write(configfile, space_around_delimiters=False)


if __name__ == "__main__":
    main()
