import json

import gardeshapi.settings
from location.models import Location, OpeningHours

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Runs a custom script to perform specific tasks.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting custom script...'))
        run()
        self.stdout.write(self.style.SUCCESS('Custom script finished.'))

import re

def convert_opening_hours(opening_hours):
    day_map = {
        "دوشنبه": 1,
        "سه‌شنبه": 2,
        "چهارشنبه": 3,
        "پنجشنبه": 4,
        "جمعه": 5,
        "شنبه": 6,
        "یکشنبه": 7
    }

    persian_to_western = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

    def normalize_time(time_str):
        time_str = time_str.translate(persian_to_western)
        # Match time like "8", "08", "8:30", "08:30"
        match = re.match(r'^(\d{1,2})(:(\d{1,2}))?$', time_str)
        if not match:
            return "00:00"

        hour = int(match.group(1))
        minute = int(match.group(3)) if match.group(3) else 0

        return f"{hour:02d}:{minute:02d}"

    result = []
    allday_count = 0
    for entry in opening_hours:
        day = entry["day"]
        hours = entry["hours"].strip()

        day_number = day_map.get(day)
        if not day_number:
            continue

        if "شبانه‌روزی" in hours:
            allday_count += 1
            open_hour = "00:00"
            close_hour = "24:00"
        else:
            parts = re.split(r"\s*تا\s*", hours)
            if len(parts) == 2:
                open_hour = normalize_time(parts[0])
                close_hour = normalize_time(parts[1])
            else:
                open_hour = close_hour = "00:00"

        result.append((day_number, (open_hour, close_hour)))
    if allday_count == 7:
        return "everyday"
    return result



def run():
    json_file = open(gardeshapi.settings.BASE_DIR / "restaurants.json", 'r', encoding='utf-8')

    data = json.load(json_file)

    created_ids = []
    open_ids = []
    for datum in data:
        helper_description = ""
        helper_description += "Additional Info:\n" + str(datum["additionalInfo"]) + "\n\n"
        helper_description += "Reviews distribution:\n" + str(datum["reviewsDistribution"]) + "\n\n"

        location_obj = Location.objects.create(title=datum['title'], address=datum['address'], phone=datum['phone'], lat=datum['location']['lat'],
                                lon=datum['location']['lng'], location_type='R', helper_description=helper_description)
        location_obj.save()
        created_ids.append(location_obj.id)
        try:
            opening_hours_json = datum['openingHours']
            result = convert_opening_hours(opening_hours_json)
            if result == "everyday":
                location_obj.always_open = True
                location_obj.save()
                continue
            for day in result:
                opening_obj = OpeningHours.objects.create(location_id=location_obj.id, day=day[0], open_time=day[1][0], close_time=day[1][1])
                opening_obj.save()
                open_ids.append(opening_obj.id)

        except Exception as e:
            pass


