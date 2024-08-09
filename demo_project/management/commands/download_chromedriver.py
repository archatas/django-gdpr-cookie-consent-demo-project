from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Downloads the latest stable ChromeDriver"

    JSON_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

    def get_platform(self):
        import sys
        import platform

        system = platform.system().lower()
        if system == "linux":
            return "linux64"
        elif system == "darwin":
            return "mac-arm64" if platform.machine() == "arm64" else "mac-x64"
        elif system == "windows":
            return "win64" if platform.machine().endswith("64") else "win32"
        else:
            self.stdout.write(
                self.style.ERROR(f"Unsupported operating system: {system}")
            )
            sys.exit(1)

    def download_file(self, url, filename):
        import requests

        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    def handle(self, *args, **options):
        import os
        import sys
        import zipfile
        import requests
        from pathlib import Path
        import shutil

        platform = self.get_platform()

        response = requests.get(self.JSON_URL)
        response.raise_for_status()
        data = response.json()

        chromedriver_url = next(
            (
                item["url"]
                for item in data["channels"]["Stable"]["downloads"]["chromedriver"]
                if item["platform"] == platform
            ),
            None,
        )

        if not chromedriver_url:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to find ChromeDriver URL for platform: {platform}"
                )
            )
            sys.exit(1)

        version = chromedriver_url.split("/")[-2]

        project_root = Path(os.getcwd())
        temp_dir = project_root / "tmp"

        zip_filename = temp_dir / f"chromedriver-{platform}.zip"
        extract_directory = temp_dir / f"chromedriver-{platform}"
        self.stdout.write(
            self.style.SUCCESS(
                f"Downloading ChromeDriver version {version} for {platform}..."
            )
        )
        self.stdout.write(chromedriver_url)
        self.download_file(chromedriver_url, zip_filename)

        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        chromedriver_name = (
            "chromedriver.exe" if platform.startswith("win") else "chromedriver"
        )
        source = extract_directory / chromedriver_name

        # Create drivers directory if it doesn't exist
        drivers_dir = project_root / "drivers"
        drivers_dir.mkdir(exist_ok=True)

        destination = drivers_dir / chromedriver_name

        # If chromedriver already exists, remove it
        if destination.exists():
            destination.unlink()

        # Move the new chromedriver to the drivers directory
        shutil.move(str(source), str(destination))

        # Delete the zip file
        os.remove(zip_filename)

        # Delete the extracted directory
        shutil.rmtree(str(extract_directory))

        if not platform.startswith("win"):
            os.chmod(destination, 0o755)

        self.stdout.write(
            self.style.SUCCESS(
                f"ChromeDriver {version} has been downloaded, extracted, and placed in the drivers directory."
            )
        )
