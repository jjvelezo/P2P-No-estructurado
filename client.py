import grpc
import torrent_pb2
import torrent_pb2_grpc

def run():
    with grpc.insecure_channel('54.234.149.53:50051') as channel:  # Cambia esta IP por la IP pública de tu instancia EC2
        stub = torrent_pb2_grpc.TorrentServiceStub(channel)
        response = stub.GetTorrent(torrent_pb2.TorrentRequest(peer_id='pavas'))
        print("Torrent received:", response)

if __name__ == '__main__':
    run()