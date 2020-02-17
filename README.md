# kitos2archimate

Flask (Pyton) app til data udveksling mellem Archimate modeller og OS2Kitos registrerede IT systemer.
Applikationen er lavet i et samarbejde mellem Favrskov (pebi@favrskov.dk) og Holstebro kommune (asl@holstebro.dk)

Scriptet kan køres med en simpel docker run
```shell
docker run --env-file=.env -p 5000:5000 kitos_tools_web
```

eller via 

```shell
docker-compose up (efter det er lavet med en build)
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
