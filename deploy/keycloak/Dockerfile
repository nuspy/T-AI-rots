# Keycloak di produzione, già "costruito" (`kc.sh build`).
#
# `kc.sh start` senza `--optimized` rifà a ogni avvio la fase di build di
# Quarkus: su un server carico sono minuti, e il pod risulta non pronto per
# tutto quel tempo. Qui le opzioni di build sono fissate nell'immagine e il pod
# parte con `start --optimized`.
#
#   docker build -f deploy/keycloak/Dockerfile -t tarots-keycloak:v7 deploy/keycloak
#
# Il tema (themes/tarots) è dentro l'immagine: ogni modifica al tema vuol dire un tag nuovo, qui e in
# deploy/k8s/tarots.yaml.
#
# Le opzioni di build (database, health, percorso) devono coincidere con quelle
# di avvio in deploy/k8s/tarots.yaml.

# Il passo di autenticazione «tarots-unione-sicura» (spi/src): compilato qui, contro i jar della stessa immagine
# Keycloak, senza Maven. Vedi spi/LEGGIMI.md.
FROM quay.io/keycloak/keycloak:26.0 AS keycloak
FROM eclipse-temurin:21-jdk AS spi
COPY --from=keycloak /opt/keycloak/lib/lib /kc
COPY spi/src /src
RUN mkdir /out \
 && javac -proc:none --release 17 -d /out -cp "/kc/main/*:/kc/boot/*" $(find /src -name '*.java') \
 && cp -r /src/META-INF /out/ \
 && jar cf /tarots-keycloak-spi.jar -C /out .

FROM quay.io/keycloak/keycloak:26.0 AS costruzione
# Anche i provider vanno copiati prima di `kc.sh build`.
COPY --from=spi /tarots-keycloak-spi.jar /opt/keycloak/providers/tarots-keycloak-spi.jar
# Il tema va copiato PRIMA di `kc.sh build`: Keycloak 26 ottimizzato include i temi nella fase di build,
# non li legge più a runtime da disco.
COPY themes/tarots /opt/keycloak/themes/tarots
ENV KC_DB=postgres \
    KC_HEALTH_ENABLED=true \
    KC_HTTP_RELATIVE_PATH=/auth
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:26.0
COPY --from=costruzione /opt/keycloak/ /opt/keycloak/
ENV KC_DB=postgres \
    KC_HEALTH_ENABLED=true \
    KC_HTTP_RELATIVE_PATH=/auth
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
