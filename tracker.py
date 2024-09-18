import grpc
from concurrent import futures
import torrent_pb2
import torrent_pb2_grpc
import threading
import random
import math
from collections import defaultdict

# Clase para Datos básicos de cada Peer
class Peer:
    def __init__(self, ip, files):
        self.ip = ip
        self.files = files

    def get_ip(self):
        return self.ip

    def get_files(self):
        return self.files

    def update_files(self, new_files):
        self.files = new_files
        print(f"Peer {self.ip} ha actualizado su lista de archivos: {new_files}")

# Estructura de datos para almacenar los peers y los archivos que poseen
class Tracker:
    def __init__(self):
        self.file_to_peers_map = defaultdict(list)
        self.peer_list = []
        self.lock = threading.Lock()
        self.replication_threshold = 10
        self.file_fragment_size = 100

    def register_peer(self, peer_ip, files):
        with self.lock:
            peer = Peer(peer_ip, files)
            self.peer_list.append(peer)
            print(f"Peer registrado: {peer.get_ip()}")

            updated_files = {}
            for file, file_size in files.items():
                original_file_name = file
                suffix = 1
                while file in self.file_to_peers_map:
                    file = f"{original_file_name}_dup{suffix}"
                    suffix += 1

                fragments = self.fragment_file(file, file_size)
                for fragment in fragments:
                    self.file_to_peers_map[fragment].append(peer)

                updated_files[file] = file_size

                if len(self.peer_list) >= self.replication_threshold:
                    self.replicate_file(fragments)

            peer.update_files(updated_files)

    def fragment_file(self, file_name, file_size):
        fragments = []
        if file_size > self.file_fragment_size:
            fragment_count = math.ceil(file_size / self.file_fragment_size)
            for i in range(fragment_count):
                fragment_size = min(self.file_fragment_size, file_size - (i * self.file_fragment_size))
                fragments.append(f"{file_name}_part{i}_size{fragment_size}MB")
            print(f"Archivo '{file_name}' fragmentado en {fragment_count} partes.")
        else:
            fragments.append(file_name)
        return fragments

    def replicate_file(self, fragments):
        available_peers = list(self.peer_list)
        random.shuffle(available_peers)
        for fragment in fragments:
            target_peer = available_peers.pop(0)
            print(f"Replicando fragmento '{fragment}' en peer {target_peer.get_ip()}")

    def search_file(self, file_name):
        with self.lock:
            result_peers = []
            found_exact_file = False

            if file_name in self.file_to_peers_map:
                found_exact_file = True
                result_peers = self.file_to_peers_map[file_name]

            if not found_exact_file:
                for key in self.file_to_peers_map:
                    if key.startswith(file_name):
                        result_peers.extend(self.file_to_peers_map[key])

                result_peers = list(set(result_peers))
            return result_peers

    def unregister_peer(self, peer_ip):
        with self.lock:
            peer_to_remove = next((p for p in self.peer_list if p.get_ip() == peer_ip), None)
            if peer_to_remove:
                self.peer_list.remove(peer_to_remove)
                for key in list(self.file_to_peers_map.keys()):
                    if peer_to_remove in self.file_to_peers_map[key]:
                        self.file_to_peers_map[key].remove(peer_to_remove)
                        if not self.file_to_peers_map[key]:
                            del self.file_to_peers_map[key]
                print(f"Peer {peer_ip} eliminado de la red.")

class TorrentService(torrent_pb2_grpc.TorrentServiceServicer):
    def __init__(self):
        self.tracker = Tracker()

    def RegisterPeer(self, request, context):
        self.tracker.register_peer(request.peer_ip, request.files)
        return torrent_pb2.PeerResponse(status="Registered successfully")

    def SearchFile(self, request, context):
        peers = self.tracker.search_file(request.file_name)
        if not peers:
            return torrent_pb2.SearchFileResponse()  # Enviar respuesta vacía si no se encuentra el archivo
        response = torrent_pb2.SearchFileResponse()
        for peer in peers:
            response.peers.add(peer_id="", peer_ip=peer.get_ip())  # Se puede omitir peer_id si no es necesario
        return response

    def UnregisterPeer(self, request, context):
        self.tracker.unregister_peer(request.peer_ip)
        return torrent_pb2.PeerResponse(status="Unregistered successfully")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    torrent_pb2_grpc.add_TorrentServiceServicer_to_server(TorrentService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Tracker server running on port 50052...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()