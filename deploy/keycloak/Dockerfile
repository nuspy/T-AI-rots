# Keycloak di produzione, già "costruito" (`kc.sh build`).
#
# `kc.sh start` senza `--optimized` rifà a ogni avvio la fase di build di
# Quarkus: su un server carico sono minuti, e il pod risulta non pronto per
# tutto quel tempo. Qui le opzioni di build sono fissate nell'immagine e il pod
# parte con `start --optimized`.
#
#   docker build -f deploy/keycloak/Dockerfile -t tarots-keycloak:v1 deploy/keycloak
#
# Le opzioni di build (database, health, percorso) devono coincidere con quelle
# di avvio in deploy/k8s/tarots.yaml.

FROM quay.io/keycloak/keycloak:26.0 AS costruzione
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
