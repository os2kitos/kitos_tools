# kitos_tools

kitos_tools er en værktøjskasse til brug sammen med KITOS. 

Projektet indeholder en række forskellige apps der alle gør brug af et fælles modul til at læse data fra KITOS.

Applikationen er lavet i et samarbejde mellem Favrskov (pebi@favrskov.dk) og Holstebro kommune (asl@holstebro.dk)

Installation
- 
```shell
git clone https://github.com/os2kitos/kitos_tools.git
cd kitos_tools
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install -e kitos_tools
pip install -r requirements.txt
pip install -r exporters/requirements.txt
```
 

# Projektstruktur

settings:
-
Den folder skal indeholde en fil med navnet "settings.json"
Denne fil læses af alle scripts og bruges til at styre indstillingerne for scripts, f.eks. brugernavn og adgangskode til Kitos, osv.


kitos_tools:
-
Generelle hjælpe funktioner og klasser til udlæsning af data fra KITOS, export til csv filer, osv.
Anvendes som et selvstændigt python modul af de øvrige scripts i projektet.

exporters:
-
Indeholder scripts der kan bruges til at eksportere data fra KITOS og gemme dem som csv filer og/eller json data, samt indlæse dem til en MySQL database.

Genereral export scriptet kan køres således:
```shell
python exporters/general_export.py
```

archimate:
-
Indeholder scripts der kan bruges til at importere IT systemer og deres relationer fra Kitos ind i en archimate model. 

IT systemer oversættes til Applications i Archimate modellen og relationer bliver til simple association relationsships.

Scriptet kan køres således:
```shell
python archimate/import_from_kitos.py --[name|id] --infile=<architemate file> --outfile=<architemate file>
```
--name eller --id angiver om der skal importeres fra Kitos ved hjælp navnet på IT Systemet eller om der skal anvendes ID fra Kitos.
Hvis det importeres til en tom archimate model eller en model hvor der allerede er importeres via navn, skal --id anvendes fremover.

service:
-
Simpel Flask (Pyton) app til udstilling af specialiserede forretningsservices på baggrund af data fra KITOS.

Scriptet kan køres direkte fra roden af projektet
```shell
python service/app.py --[prod|test] --username=<user> --password=<password>
```

Det kan også køres med en simpel docker run
```shell
docker run --env-file=.env -p 5000:5000 kitos_tools_web
```

eller via

```shell
docker-compose up 
```
efter der er lavet et image med 

```shell
docker build -t kitos_tools .
```


Filen ".env-example" viser hvordan lokale variabler bliver sat, så man kan holde brugernavne ude af git commits (den rigtige .env fil bør ikke være med i git eller docker)
```.env
# Kitos standard settings
KITOS_USER=brugernavn
KITOS_PASSWORD=password
KITOS_URL=url_til_kitos

# hvis flask debug sættes til 1 så kører flask i debug mode
FLASK_DEBUG="1"
```

Ideen bag denne .env fil er, at man undgår at have brugernavn og password i selve docker imaget. Dermed er det nemmere at tilpasse en kørende installation 
hvor man nemt kan skifte brugernavn eller password uden at der skla bygges og deployes et nyt docker image

Der er i skrivende stund ikke et image klar til download, så man er nødt til selv at bygge et image.
