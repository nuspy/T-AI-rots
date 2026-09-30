"""Un server SFTP finto per i test del backup: paramiko in un thread, su 127.0.0.1, che serve una cartella locale
come se fosse il NAS. Accetta una sola chiave pubblica (quella del test) e ha la sua chiave dell'host."""
from __future__ import annotations

import os
import socket
import threading
from pathlib import Path
from typing import List

import paramiko
from paramiko import SFTPAttributes, SFTPHandle, SFTPServer, SFTPServerInterface


class _Accesso(paramiko.ServerInterface):
    def __init__(self, chiave_ammessa: paramiko.PKey) -> None:
        self._chiave = chiave_ammessa

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL if key.asbytes() == self._chiave.asbytes() else paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "publickey"

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED if kind == "session" else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED


class _Handle(SFTPHandle):
    def stat(self):
        try:
            return SFTPAttributes.from_stat(os.fstat(self.readfile.fileno()))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def chattr(self, attr):
        return paramiko.SFTP_OK


def _cartella_sftp(radice: Path):
    class Cartella(SFTPServerInterface):
        def _vero(self, percorso: str) -> str:
            return str(radice / self.canonicalize(percorso).lstrip("/"))

        def list_folder(self, path):
            try:
                out = []
                for nome in os.listdir(self._vero(path)):
                    a = SFTPAttributes.from_stat(os.stat(os.path.join(self._vero(path), nome)))
                    a.filename = nome
                    out.append(a)
                return out
            except OSError as e:
                return SFTPServer.convert_errno(e.errno)

        def stat(self, path):
            try:
                return SFTPAttributes.from_stat(os.stat(self._vero(path)))
            except OSError as e:
                return SFTPServer.convert_errno(e.errno)

        lstat = stat

        def open(self, path, flags, attr):
            vero = self._vero(path)
            try:
                fd = os.open(vero, flags | getattr(os, "O_BINARY", 0), 0o666)
            except OSError as e:
                return SFTPServer.convert_errno(e.errno)
            if flags & os.O_WRONLY:
                modo = "ab" if flags & os.O_APPEND else "wb"
            elif flags & os.O_RDWR:
                modo = "a+b" if flags & os.O_APPEND else "r+b"
            else:
                modo = "rb"
            f = os.fdopen(fd, modo)
            h = _Handle(flags)
            h.filename, h.readfile, h.writefile = vero, f, f
            return h

        def remove(self, path):
            try:
                os.remove(self._vero(path))
            except OSError as e:
                return SFTPServer.convert_errno(e.errno)
            return paramiko.SFTP_OK

        def rename(self, oldpath, newpath):
            try:
                os.rename(self._vero(oldpath), self._vero(newpath))
            except OSError as e:
                return SFTPServer.convert_errno(e.errno)
            return paramiko.SFTP_OK

        def mkdir(self, path, attr):
            try:
                os.mkdir(self._vero(path))
            except OSError as e:
                return SFTPServer.convert_errno(e.errno)
            return paramiko.SFTP_OK

        def chattr(self, path, attr):
            return paramiko.SFTP_OK

    return Cartella


class ServerSftpFinto:
    def __init__(self, radice: Path, chiave_client: paramiko.PKey) -> None:
        self.radice = radice
        self.chiave_host = paramiko.RSAKey.generate(2048)
        self._chiave_client = chiave_client
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(8)
        self.porta = self._sock.getsockname()[1]
        self._trasporti: List[paramiko.Transport] = []
        self._fermo = threading.Event()
        self._thread = threading.Thread(target=self._accetta, daemon=True)

    def avvia(self) -> "ServerSftpFinto":
        self._thread.start()
        return self

    def _accetta(self) -> None:
        self._sock.settimeout(0.2)
        while not self._fermo.is_set():
            try:
                conn, _ = self._sock.accept()
            except (socket.timeout, OSError):
                continue
            t = paramiko.Transport(conn)
            t.add_server_key(self.chiave_host)
            t.set_subsystem_handler("sftp", SFTPServer, _cartella_sftp(self.radice))
            try:
                t.start_server(server=_Accesso(self._chiave_client))
            except (paramiko.SSHException, OSError, EOFError):
                continue  # il client ha chiuso (chiave dell'host rifiutata, accesso negato): normale nei test
            self._trasporti.append(t)

    def ferma(self) -> None:
        self._fermo.set()
        for t in self._trasporti:
            t.close()
        self._sock.close()
        self._thread.join(timeout=2)
