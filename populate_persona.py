import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "azureproject.settings")

import django

django.setup()

import csv
from restaurant_review.models import Persona


def populate(N):
    with open("persona.csv", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Columnas: {", ".join(row)}')
                line_count += 1
            else:
                id_tipo = "CC"
                id_num = row[0]
                nom_persona = row[1]
                persona = Persona.objects.get_or_create(id_tipo=id_tipo, id_num=id_num, nom_persona=nom_persona)[0]

                line_count += 1

            if line_count > N:
                break

        print(f"Processed {line_count} lines.")


if __name__ == "__main__":
    print("populating script!")
    populate(5000)
    print("populating complete!")
