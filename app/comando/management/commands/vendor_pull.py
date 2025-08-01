import helpers
from django.core.management.base import BaseCommand
from typing import Any
from django.conf import settings

STATICFILES_VENDOR_DIR = getattr(settings, 'STATICFILES_VENDOR_DIR')

VENDOR_STATIC_FILES = {
    "flowbite.min.css":"https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.css",
    "flowbite.min.js": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js",
}

class Command(BaseCommand):
    def handle(self, *args:Any, **options: Any):
        self.stdout.write("Downloading vendor static files...")
        completed_urls = []

        for name, url in VENDOR_STATIC_FILES.items():
            out_path = STATICFILES_VENDOR_DIR / name
            dl_success = helpers.downloader.download_to_local(url, out_path)
            if dl_success:
                completed_urls.append(url)
                self.stdout.write(f"Downloaded {name} to {out_path}")
            else:
                self.stdout.write(f"Failed to download {name} from {url}")
            
            if set(completed_urls) == set(VENDOR_STATIC_FILES.values()):
                self.stdout.write("All vendor static files downloaded successfully.")