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
        print(f"Registrando peer con IP: {peer_ip}")  # Verifica aquí
        with self.lock:
            peer = Peer(peer_ip, files)
            self.peer_list.append(peer)
            print(f"Peer registrado: {peer.get_ip()}")

            updated_files = {}
            # Iterar sobre los archivos recibidos (RepeatedCompositeContainer o diccionario)
            for file in files:
                file_name = file.file_name  # Asegúrate de que file tiene los atributos correctos
                file_size = file.file_size
                original_file_name = file_name
                suffix = 1
                while file_name in self.file_to_peers_map:
                    file_name = f"{original_file_name}_dup{suffix}"
                    suffix += 1

                # Fragmentar el archivo
                fragments = self.fragment_file(file_name, file_size)
                updated_files[file_name] = fragments  # Guardar los fragmentos en lugar del archivo completo

                # Asociar fragmentos con el peer
                for fragment in fragments:
                    self.file_to_peers_map[fragment['name']].append(peer)

                # Replicar fragmentos si es necesario
                if len(self.peer_list) >= self.replication_threshold:
                    self.replicate_file(fragments)

            peer.update_files(updated_files)
            
            # Imprimir la lista de archivos referenciados del peer
            print(f"Lista de archivos actualizada para el peer {peer.get_ip()}: {peer.get_files()}")

            return updated_files  # Devolver la lista actualizada para enviarla al peer

    def fragment_file(self, file_name, file_size):
        fragments = []
        if file_size > self.file_fragment_size:
            fragment_count = math.ceil(file_size / self.file_fragment_size)
            for i in range(fragment_count):
                fragment_size = min(self.file_fragment_size, file_size - (i * self.file_fragment_size))
                
                # Guardar el fragmento como un diccionario con nombre y tamaño separados
                fragments.append({
                    'name': f"{file_name}_part{i}",
                    'size': fragment_size
                })
            print(f"Archivo '{file_name}' fragmentado en {fragment_count} partes.")
        else:
            fragments.append({
                'name': file_name,
                'size': file_size
            })
        print(f"Fragmentos: {fragments}")
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
            print(f"Lista de peers antes de desregistrar: {[p.get_ip() for p in self.peer_list]}")
            
            peer_to_remove = next((p for p in self.peer_list if p.get_ip() == peer_ip), None)
        
            if peer_to_remove:
                
                # Imprimir los archivos asociados al peer antes de eliminarlo
                archivos_ligados = [key for key, peers in self.file_to_peers_map.items() if peer_to_remove in peers]
                if archivos_ligados:
                    print(f"Archivos ligados al peer {peer_ip} antes de eliminar:")
                    for archivo in archivos_ligados:
                        print(f"- {archivo}")
                else:
                    print(f"No hay archivos ligados al peer {peer_ip}.")
                
                self.peer_list.remove(peer_to_remove)
            
                # Eliminar los archivos relacionados con el peer
                for key in list(self.file_to_peers_map.keys()):
                    if peer_to_remove in self.file_to_peers_map[key]:
                        self.file_to_peers_map[key].remove(peer_to_remove)
                    
                        if not self.file_to_peers_map[key]:  # Si no hay más peers con el archivo, eliminar el archivo del tracker
                            del self.file_to_peers_map[key]
                            print(f"Archivo {key} completamente eliminado del tracker.")
                        
                print(f"Peer {peer_ip} eliminado de la red.")
            else:
                print(f"Peer {peer_ip} no encontrado.")
                
        # Código para desregistrar...
        print(f"Lista de peers después de desregistrar: {[p.get_ip() for p in self.peer_list]}")

class TorrentService(torrent_pb2_grpc.TorrentServiceServicer):
    def __init__(self):
        self.tracker = Tracker()

    def RegisterPeer(self, request, context):
        updated_files = self.tracker.register_peer(request.peer_ip, request.files)

        # Crear la respuesta del peer con los archivos actualizados
        response = torrent_pb2.PeerResponse(status="Registered successfully")

        # Añadir los archivos fragmentados a la respuesta
        for file_name, file_fragments in updated_files.items():
            for fragment in file_fragments:
                # Asegurarte de que estás accediendo a los atributos correctos del fragmento
                response.updated_files.add(file_name=fragment['name'], file_size=fragment['size'])  # Usar fragment['name'] y fragment['size']
    
        return response

    def SearchFile(self, request, context):
        peers = self.tracker.search_file(request.file_name)
        if not peers:
            return torrent_pb2.SearchFileResponse()  # Enviar respuesta vacía si no se encuentra el archivo
        response = torrent_pb2.SearchFileResponse()
        for peer in peers:
            response.peers.add(peer_ip=peer.get_ip())  # Solo se usa peer_ip
        return response

    def UnregisterPeer(self, request, context):
        peer_ip = request.peer_ip
        if not any(peer.get_ip() == peer_ip for peer in self.tracker.peer_list):
            return torrent_pb2.PeerResponse(status="Peer not found")

        self.tracker.unregister_peer(peer_ip)
        return torrent_pb2.PeerResponse(status="Unregistered successfully")
    
    def UploadFile(self, request, context):
        peer_ip = request.peer_ip
        file_name = request.file_name
        file_size = request.file_size
        print(f"Received upload request: {file_name} from {peer_ip} (size: {file_size})")
    
        return torrent_pb2.UploadFileResponse(status="Upload successful")  # Retorna solo el estado
    
    def GetFile(self, request, context):
        file_name = request.file_name
        peers = self.tracker.search_file(file_name)
        if not peers:
            return torrent_pb2.GetFileResponse()  # Devolver respuesta vacía si no se encuentra el archivo
        # Asumiendo que se devuelva el primer peer que tiene el archivo
        peer_info = peers[0]
        return torrent_pb2.GetFileResponse(peer=torrent_pb2.PeerInfo(peer_ip=peer_info.get_ip()))  # Solo se usa peer_ip


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    torrent_pb2_grpc.add_TorrentServiceServicer_to_server(TorrentService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Tracker server running on port 50052...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()