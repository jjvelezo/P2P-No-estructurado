import grpc
from concurrent import futures
import torrent_pb2
import torrent_pb2_grpc

# Datos del archivo .torrent (puede ser JSON u otro formato)
TORRENT_DATA = {
    "info": "Some info about the torrent"
}

# Configura aquí la IP y puerto del tracker
TRACKER_INFO = {
    "tracker_ip": "44.210.100.174",  # IP del tracker
    "tracker_port": "50052"  # Puerto del tracker
}

class TorrentService(torrent_pb2_grpc.TorrentServiceServicer):
    def GetTorrent(self, request, context):
        peer_ip = request.peer_ip  # Recibir la IP del peer
        print(f"Received request from peer with IP: {peer_ip}")
        
        # Agregar la IP del peer al campo `torrent_data`
        response_data = {
            "torrent_data": TORRENT_DATA,
            "peer_ip": peer_ip,  # Aquí añadimos la IP del peer que solicitó
            "tracker_ip": TRACKER_INFO["tracker_ip"],
            "tracker_port": TRACKER_INFO["tracker_port"]
        }

        return torrent_pb2.TorrentResponse(torrent_data=str(response_data), tracker_ip=TRACKER_INFO["tracker_ip"], tracker_port=TRACKER_INFO["tracker_port"])

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    torrent_pb2_grpc.add_TorrentServiceServicer_to_server(TorrentService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server running on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve_grpc()