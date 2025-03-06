# How to get location

location could be found in JSON under the field:
mapaOsmUrl or mapaGoogleUrl where is location address built into URL

"mapaGoogleUrl": "https://maps.google.pl/maps?q=Warszawa%2C%20Radomska%2C%20%2013%2F21%2C%20Warszawa%2C%20mazowieckie%2C%20Warszawa%2C%20Polska",
"mapaOsmUrl": "https://www.openstreetmap.org/search?query=Radomska%2C%20%2013%2F21%2C%20Warszawa%2C%20mazowieckie%2C%20Polska"

Radomska%2C%20%2013%2F21%2C%20Warszawa%2C%20mazowieckie%2C%20Polska
Radomska,  13/21, Warszawa, mazowieckie, Polska

street: "Radomska"
building: "13/21"
city: "Warszawa"
district: "mazowieckie"
country: "Polska"

# Установим локальный сервер Nominatim
Поставим Docker (Windows - должен быть включен Linux для Windows подсистема - Windows Features)

-------------------------------------------------------
# Соберем Docker образ Nominatim:
--------------------------------------------------------
# Склонируем репозиторий Nominatim

git clone https://github.com/mediagis/nominatim-docker.git
cd nominatim-docker
dir

"""
Directory of E:\!___INSTALL\PROGRAMMING\Docker\Nominatim\nominatim-docker

21.01.2025  17:28    <DIR>          .
21.01.2025  17:28    <DIR>          ..
21.01.2025  17:28            12 648 .all-contributorsrc
21.01.2025  17:28    <DIR>          .github
21.01.2025  17:28                10 .gitignore
21.01.2025  17:28    <DIR>          2.5
21.01.2025  17:28    <DIR>          3.0
21.01.2025  17:28    <DIR>          3.1
21.01.2025  17:28    <DIR>          3.2
21.01.2025  17:28    <DIR>          3.3
21.01.2025  17:28    <DIR>          3.4
21.01.2025  17:28    <DIR>          3.5
21.01.2025  17:28    <DIR>          3.6
21.01.2025  17:28    <DIR>          3.7
21.01.2025  17:28    <DIR>          4.0
21.01.2025  17:28    <DIR>          4.1
21.01.2025  17:28    <DIR>          4.2
21.01.2025  17:28    <DIR>          4.3
21.01.2025  17:28    <DIR>          4.4
21.01.2025  17:28    <DIR>          4.5
21.01.2025  17:28             7 169 LICENSE
21.01.2025  17:28            23 393 README.md
               4 File(s)         43 220 bytes
              18 Dir(s)  494 415 167 488 bytes free
"""

------------------------------------------------------------------------
# Забилдим образ Nominatim необходимой версии

cd 4.5
docker build -t nominatim:4.5 .

"""
 Directory of E:\!___INSTALL\PROGRAMMING\Docker\Nominatim\nominatim-docker

21.01.2025  17:28    <DIR>          .
21.01.2025  17:28    <DIR>          ..
21.01.2025  17:28            12 648 .all-contributorsrc
21.01.2025  17:28    <DIR>          .github
21.01.2025  17:28                10 .gitignore
21.01.2025  17:28    <DIR>          2.5
21.01.2025  17:28    <DIR>          3.0
21.01.2025  17:28    <DIR>          3.1
21.01.2025  17:28    <DIR>          3.2
21.01.2025  17:28    <DIR>          3.3
21.01.2025  17:28    <DIR>          3.4
21.01.2025  17:28    <DIR>          3.5
21.01.2025  17:28    <DIR>          3.6
21.01.2025  17:28    <DIR>          3.7
21.01.2025  17:28    <DIR>          4.0
21.01.2025  17:28    <DIR>          4.1
21.01.2025  17:28    <DIR>          4.2
21.01.2025  17:28    <DIR>          4.3
21.01.2025  17:28    <DIR>          4.4
21.01.2025  17:28    <DIR>          4.5
21.01.2025  17:28             7 169 LICENSE
21.01.2025  17:28            23 393 README.md
               4 File(s)         43 220 bytes
              18 Dir(s)  494 415 167 488 bytes free

[+] Building 363.8s (20/20) FINISHED                                                               docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                               0.1s
 => => transferring dockerfile: 3.10kB                                                                             0.0s
 => [internal] load metadata for docker.io/library/ubuntu:24.04                                                    2.5s
 => [auth] library/ubuntu:pull token for registry-1.docker.io                                                      0.0s
 => [internal] load .dockerignore                                                                                  0.0s
 => => transferring context: 2B                                                                                    0.0s
 => [internal] load build context                                                                                  0.1s
 => => transferring context: 13.08kB                                                                               0.0s
 => [build  1/11] FROM docker.io/library/ubuntu:24.04@sha256:80dd3c3b9c6cecb9f1667e9290b3bc61b78c2678c02cbdae5f0f  6.5s
 => => resolve docker.io/library/ubuntu:24.04@sha256:80dd3c3b9c6cecb9f1667e9290b3bc61b78c2678c02cbdae5f0fea92cc67  0.1s
 => => sha256:de44b265507ae44b212defcb50694d666f136b35c1090d9709068bc861bb2d64 29.75MB / 29.75MB                   5.0s
 => => extracting sha256:de44b265507ae44b212defcb50694d666f136b35c1090d9709068bc861bb2d64                          1.3s
 => [build  2/11] WORKDIR /app                                                                                     0.1s
 => [build  3/11] RUN      --mount=type=cache,target=/var/cache/apt,sharing=locked     --mount=type=cache,targe  128.7s
 => [build  4/11] RUN true     && echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/16/main/pg_hba.conf     &&  0.6s
 => [build  5/11] RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked pip install --break-system-pack  106.7s
 => [build  6/11] RUN true     && apt-get -y remove --purge --auto-remove         build-essential         postgre  1.4s
 => [build  7/11] COPY conf.d/postgres-import.conf /etc/postgresql/16/main/conf.d/postgres-import.conf.disabled    0.1s
 => [build  8/11] COPY conf.d/postgres-tuning.conf /etc/postgresql/16/main/conf.d/                                 0.1s
 => [build  9/11] COPY config.sh /app/config.sh                                                                    0.1s
 => [build 10/11] COPY init.sh /app/init.sh                                                                        0.1s
 => [build 11/11] COPY start.sh /app/start.sh                                                                      0.1s
 => [stage-1 1/3] COPY --from=build / /                                                                            5.0s
 => [stage-1 2/3] WORKDIR /app                                                                                     1.0s
 => [stage-1 3/3] COPY conf.d/env /nominatim/.env                                                                  0.1s
 => exporting to image                                                                                           103.5s
 => => exporting layers                                                                                           84.2s
 => => exporting manifest sha256:d665f44d1be1141838d256feb63417c716e1d7bfcd3e7ab71528a6e5438dd50c                  0.0s
 => => exporting config sha256:2783b4ccbf9f94171b5110b3511b3c09c53c3760e11aa5ac424399cf40bdc24c                    0.0s
 => => exporting attestation manifest sha256:e76244ae4f16fcb9af3da216708c9a763ff58283c84fcd108dd5bd84fc41af39      0.0s
 => => exporting manifest list sha256:bd184cabfe788d9ddff1a9b51300a02bd3fb32eb15b1cb3a7062aa2c2e72be9f             0.0s
 => => naming to docker.io/library/nominatim:4.5                                                                   0.0s
 => => unpacking to docker.io/library/nominatim:4.5                                                               19.2s

 1 warning found (use docker --debug to expand):
 - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ENV "NOMINATIM_PASSWORD") (line 94)
 """

 -------------------------------------------------------
# Используем существующий docker-compose.yml

cmd>cd E:\!___INSTALL\PROGRAMMING\Docker\Nominatim\nominatim-docker\4.5\contrib
cmd>notepad docker-compose.yml

"""
version: "3"

services:
    nominatim:
        container_name: nominatim
        image: mediagis/nominatim:4.5
        ports:
            - "8080:8080"
        environment:
            # see https://github.com/mediagis/nominatim-docker/tree/master/4.5#configuration for more options
            PBF_URL: https://download.geofabrik.de/europe/poland/mazowieckie-latest.osm.pbf
            REPLICATION_URL: https://download.geofabrik.de/europe/poland-updates/
            NOMINATIM_PASSWORD: mypassword
        volumes:
            - nominatim-data:/var/lib/postgresql/16/main
        shm_size: 1gb

volumes:
    nominatim-data:
"""

Редактирование параметров:
 - Установим ссылку на PBF файл Nominatim используемыми данными региона: PBF_URL - берётся с сайта geofabrik
 - Установим пароль для POSTGRES базы данных: NOMINATIM_PASSWORD - mypassword
 - Порт 8080 не конфликтует с другими сервисами на вашей машине. Если конфликт есть, измените его.

 -----------------------------

# Соберём образ Nominatim находясь в директории с только что созданным docker-compose.yml

cmd> docker-compose up

Пришлось довольно долго подождать...

------------------------------
# Сервер запущен - выполним пробный запрос

http://localhost:8080/search?q=Warsaw%20Pustola%2025&format=json

или

http://localhost:8080/reverse?lat=52.2297&lon=21.0122&format=json

Всё работает:
[
{14 entries
    place_id: 431880,
    licence: "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
    osm_type: "way",
    osm_id: 164580124,
    lat: "52.2321841",
    lon: "20.935230422848832",
    class: "building",
    type: "apartments",
    place_rank: 30,
    importance: 0.00000999999999995449,
    addresstype: "building",
    name: "",
    display_name: "25, Pustola, Osiedle Mszczonowska, Ulrychów, Воля, Warsaw, Masovian Voivodeship, 01-107, Poland",
    boundingbox: [4 elements
"52.2320328",
"52.2323228",
"20.9345540",
"20.9358392"
]
}
]