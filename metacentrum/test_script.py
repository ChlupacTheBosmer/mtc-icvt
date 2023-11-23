import datetime
import pkg_resources

def main():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    installed_packages = [d.project_name for d in pkg_resources.working_set]

    with open("test_output.txt", "w") as file:
        file.write(f"Script ran successfully at {timestamp}\n")
        file.write("Installed Python packages:\n")
        for package in installed_packages:
            file.write(f"{package}\n")

if __name__ == "__main__":
    main()