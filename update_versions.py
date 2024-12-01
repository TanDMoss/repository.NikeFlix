import os
import re

def get_current_version(file_path, version_pattern):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            content = file.read()
        match = re.search(version_pattern, content)
        if match:
            return match.group(1)
    return "Unknown"

def update_version_in_addon(file_path, new_version):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            lines = file.readlines()
        
        # Update the version in the second line only
        updated_lines = []
        for i, line in enumerate(lines):
            if i == 1:  # Second line (0-based index)
                line = re.sub(r'(version=")(\d+\.\d+\.\d+)(")', f'\\1{new_version}\\3', line)
            updated_lines.append(line)
        
        with open(file_path, "w") as file:
            file.writelines(updated_lines)
        print(f"Updated version in {file_path} to {new_version}.")
    else:
        print(f"{file_path} not found!")

def update_version_in_builds(file_path, version_pattern, new_version):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            content = file.read()
        # Replace all occurrences of the version pattern
        content = re.sub(version_pattern, lambda m: f'{m.group(1)}{new_version}{m.group(3)}', content)
        with open(file_path, "w") as file:
            file.write(content)
        print(f"Updated version in {file_path} to {new_version}.")
    else:
        print(f"{file_path} not found!")

def main():
    # Paths to the files
    wizard_addon_file = "./repo/plugin.program.nikeflixwizard/addon.xml"
    wizard_builds_file = "./repo/plugin.program.nikeflixwizard/resources/text/builds.txt"

    # Patterns for matching versions in builds.txt
    version_pattern = r'(version=")(\d+\.\d+\.\d+)(")'

    # Display current versions
    wizard_addon_version = get_current_version(wizard_addon_file, r'version="(\d+\.\d+\.\d+)"')
    wizard_builds_version = get_current_version(wizard_builds_file, version_pattern)

    print(f"Current version in plugin.program.nikeflixwizard addon.xml: {wizard_addon_version}")
    print(f"Current version in plugin.program.nikeflixwizard builds.txt: {wizard_builds_version}")

    # Get new version from user
    new_version = input("Enter the new version number (e.g., 2.2.9): ")

    # Update versions
    update_version_in_addon(wizard_addon_file, new_version)
    update_version_in_builds(wizard_builds_file, version_pattern, new_version)

    print("All tasks completed!")

if __name__ == "__main__":
    main()