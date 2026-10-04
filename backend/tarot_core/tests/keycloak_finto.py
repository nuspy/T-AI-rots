"""Un Keycloak finto (HTTP in memoria) per l'accesso dalle app (v9, Fase 6): utenti, identità social collegate,
attributi, sessioni, identity provider, flussi (quanto basta) e l'importazione parziale dei client.

Fa ciò che fa quello vero per quanto serve qui, verificato su un Keycloak 26.0.8:

- `PUT /users/{id}` senza l'email viene rifiutato (profilo utente dichiarativo): va mandata la rappresentazione intera;
- un'identità social appartiene a un solo utente, e un utente ha al più un'identità per provider (409);
- `POST /clients` è vietato all'account di servizio (manca `manage-clients`), `POST /partialImport` no;
- il segreto di un provider torna mascherato, e rimandarlo mascherato tiene quello di prima.
"""
from __future__ import annotations

import copy
import json
from typing import Any, Dict, List, Optional

import httpx

from tarot_core.auth.keycloak_admin import KeycloakAdmin, PASSO_UNIONE_SICURA
from tarot_core.auth.provider_sociali import FLUSSO_UNIONE, MASCHERA
from tarot_core.settings import Settings

PREFISSO = "/auth/admin/realms/tarots"


class KeycloakFinto:
    def __init__(self) -> None:
        self.utenti: Dict[str, Dict[str, Any]] = {}
        self.identita: Dict[str, List[Dict[str, Any]]] = {}
        self.provider: Dict[str, Dict[str, Any]] = {}
        self.client: Dict[str, Dict[str, Any]] = {}
        self.scritture: List[tuple] = []
        self.logout: List[str] = []
        #: Fa fallire (500) il collegamento di un'identità a questo utente: per provare il ritorno allo stato di prima.
        self.collega_fallisce_per: Optional[str] = None
        self.giu = False

    def aggiungi_utente(self, sub: str, email: str, *, identita: Optional[List[Dict[str, Any]]] = None) -> None:
        self.utenti[sub] = {"id": sub, "username": email, "email": email, "enabled": True, "emailVerified": True,
                            "access": {"manage": True}, "federatedIdentities": []}
        self.identita[sub] = list(identita or [])

    def _proprietario(self, alias: str, id_social: str) -> Optional[str]:
        for sub, elenco in self.identita.items():
            if any(i["identityProvider"] == alias and i["userId"] == id_social for i in elenco):
                return sub
        return None

    def _mascherato(self, p: Dict[str, Any]) -> Dict[str, Any]:
        p = copy.deepcopy(p)
        if p.get("config", {}).get("clientSecret"):
            p["config"]["clientSecret"] = MASCHERA
        return p

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if self.giu:
            raise httpx.ConnectError("Keycloak spento")
        percorso = request.url.path
        if percorso.endswith("/protocol/openid-connect/token"):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 300})
        assert request.headers.get("authorization") == "Bearer tok"
        corpo = json.loads(request.content) if request.content else None
        if request.method != "GET":
            self.scritture.append((request.method, percorso[len(PREFISSO):], corpo))
        resto = percorso[len(PREFISSO):]
        metodo = request.method

        if resto == "/clients" and metodo == "POST":
            return httpx.Response(403, json={"error": "HTTP 403 Forbidden"})
        if resto == "/partialImport":
            risultati = []
            for c in corpo.get("clients", []):
                if c["clientId"] in self.client:
                    risultati.append({"action": "SKIPPED", "resourceType": "CLIENT", "resourceName": c["clientId"]})
                else:
                    self.client[c["clientId"]] = c
                    risultati.append({"action": "ADDED", "resourceType": "CLIENT", "resourceName": c["clientId"]})
            return httpx.Response(200, json={"results": risultati})

        if resto == "/authentication/flows":
            return httpx.Response(200, json=[{"alias": a, "id": a} for a in ("browser", FLUSSO_UNIONE)])
        if resto.startswith("/authentication/flows/") and resto.endswith("/executions"):
            # Il flusso dell'unione c'è già, col passo sicuro: `assicura_flusso_unione` non deve cambiare niente.
            return httpx.Response(200, json=[{"id": "p1", "providerId": PASSO_UNIONE_SICURA, "requirement": "ALTERNATIVE"}])

        if resto == "/identity-provider/instances":
            if metodo == "GET":
                return httpx.Response(200, json=[self._mascherato(p) for p in self.provider.values()])
            self.provider[corpo["alias"]] = corpo
            return httpx.Response(201)
        if resto.startswith("/identity-provider/instances/"):
            alias = resto.rsplit("/", 1)[1]
            if alias not in self.provider:
                return httpx.Response(404, json={"error": "Could not find identity provider"})
            if metodo == "GET":
                return httpx.Response(200, json=self._mascherato(self.provider[alias]))
            if corpo["config"].get("clientSecret") == MASCHERA:
                corpo["config"]["clientSecret"] = self.provider[alias]["config"].get("clientSecret")
            self.provider[alias] = corpo
            return httpx.Response(204)

        if resto.startswith("/sessions/"):
            return httpx.Response(204)
        if resto.startswith("/users/"):
            parti = resto.split("/")  # ['', 'users', sub, ...]
            sub = parti[2]
            if sub not in self.utenti:
                return httpx.Response(404, json={"error": "User not found"})
            coda = parti[3:]
            if not coda:
                if metodo == "GET":
                    u = copy.deepcopy(self.utenti[sub])
                    u["federatedIdentities"] = copy.deepcopy(self.identita[sub])
                    return httpx.Response(200, json=u)
                if metodo == "PUT":
                    if not corpo.get("email"):
                        return httpx.Response(400, json={"field": "email", "errorMessage": "error-user-attribute-required"})
                    self.utenti[sub].update({k: v for k, v in corpo.items() if k in ("enabled", "attributes", "email",
                                                                                      "firstName", "lastName")})
                    return httpx.Response(204)
            if coda == ["federated-identity"]:
                return httpx.Response(200, json=copy.deepcopy(self.identita[sub]))
            if len(coda) == 2 and coda[0] == "federated-identity":
                alias = coda[1]
                if metodo == "DELETE":
                    prima = len(self.identita[sub])
                    self.identita[sub] = [i for i in self.identita[sub] if i["identityProvider"] != alias]
                    return httpx.Response(204 if len(self.identita[sub]) < prima else 404)
                if metodo == "POST":
                    if sub == self.collega_fallisce_per:
                        return httpx.Response(500, json={"error": "unknown_error"})
                    if any(i["identityProvider"] == alias for i in self.identita[sub]) or \
                            self._proprietario(alias, corpo["userId"]):
                        return httpx.Response(409, json={"errorMessage": "User is already linked with provider"})
                    self.identita[sub].append({"identityProvider": alias, "userId": corpo["userId"],
                                               "userName": corpo.get("userName", "")})
                    return httpx.Response(204)
            if coda == ["sessions"]:
                return httpx.Response(200, json=[])
            if coda == ["logout"]:
                self.logout.append(sub)
                return httpx.Response(204)
            if coda and coda[0] == "consents":
                return httpx.Response(204)
        return httpx.Response(404)

    def fabbrica(self):
        def crea() -> KeycloakAdmin:
            impostazioni = Settings(
                keycloak_url="http://kc.interno:8080/auth", keycloak_issuer_url="https://tarots.chat/auth",
                keycloak_realm="tarots", keycloak_client_secret="segreto-api",
            )
            return KeycloakAdmin(impostazioni, transport=httpx.MockTransport(self))
        return crea
