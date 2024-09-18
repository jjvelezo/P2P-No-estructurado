import java.util.*;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/* 
 * Este Documento es la base del racker, permite ruebas de escritorio
 * 
 */

class Peer {
    // Clase para Datos básicos de cada Peer

    String ip; // direccion IP
    Map<String, Integer> files; // lista de archivos (no son archivos reales)

    public Peer(String ip, Map<String, Integer> files) {
        this.ip = ip;
        this.files = files;
    }

    public String getIp() {
        // Retorna direccion IP del peer
        return ip;
    }

    public Map<String, Integer> getFiles() {
        // Retorna la lsita de archivos compartidos por el peer
        return files;
    }

    // Método para actualizar la lista de archivos en el peer
    public void updateFiles(Map<String, Integer> newFiles) {
        this.files = newFiles;
        System.out.println("Peer " + ip + " ha actualizado su lista de archivos: " + newFiles);
    }
}

class Tracker {
    // Estructura de datos para almacenar los peers y los archivos que poseen

    private Map<String, List<Peer>> fileToPeersMap; // El Map asicia nombres de archivos con listas de peers que tiene
                                                    // el archivo
    private List<Peer> peerList; // Lista de peers en la red
    private Lock lock; // lock para garantizar acceso concurrente seguro (Consistencia)

    private int replicationThreshold = 10; // Umbral para replicación
    private int fileFragmentSize = 100; // Tamaño máximo de cada fragmento en MB

    public Tracker() {
        fileToPeersMap = new HashMap<>();
        peerList = new ArrayList<>();
        lock = new ReentrantLock();
    }

    // Registro de un nuevo peer
    public void registerPeer(Peer peer) {
        lock.lock();
        try {
            // Agregar el peer a la lista de peers
            peerList.add(peer);
            System.out.println("Peer registrado: " + peer.getIp());

            // Registrar archivos del peer
            Map<String, Integer> updatedFiles = new HashMap<>();
            for (Map.Entry<String, Integer> entry : peer.getFiles().entrySet()) {
                String file = entry.getKey();
                int fileSize = entry.getValue();

                // Verificar si el archivo ya existe en el tracker
                String originalFileName = file;
                int suffix = 1;
                while (fileToPeersMap.containsKey(file)) {
                    file = originalFileName + "_dup" + suffix++;
                }

                // Fragmentar si el archivo es muy grande
                List<String> fragments = fragmentFile(file, fileSize);
                for (String fragment : fragments) {
                    fileToPeersMap.putIfAbsent(fragment, new ArrayList<>());
                    fileToPeersMap.get(fragment).add(peer);
                }

                // Actualizar la lista de archivos del peer
                updatedFiles.put(file, fileSize);

                // Replicar si el número de peers supera el umbral
                if (peerList.size() >= replicationThreshold) {
                    replicateFile(fragments);
                }
            }

            // Actualizar archivos en el peer
            peer.updateFiles(updatedFiles);

        } finally {
            lock.unlock();
        }
    }

    // Fragmenta el archivo si su tamaño es mayor al fragment size
    private List<String> fragmentFile(String fileName, int fileSize) {
        List<String> fragments = new ArrayList<>();
        if (fileSize > fileFragmentSize) {
            int fragmentCount = (int) Math.ceil((double) fileSize / fileFragmentSize);

            for (int i = 0; i < fragmentCount; i++) {
                int fragmentSize = Math.min(fileFragmentSize, fileSize - (i * fileFragmentSize));
                fragments.add(fileName + "_part" + i + "_size" + fragmentSize + "MB");
            }

            System.out.println("Archivo '" + fileName + "' fragmentado en " + fragmentCount + " partes.");
        } else {
            fragments.add(fileName);
        }
        return fragments;
    }

    // Replicación de los fragmentos del archivo
    private void replicateFile(List<String> fragments) {
        List<Peer> availablePeers = new ArrayList<>(peerList); // Copia de peers disponibles
        Collections.shuffle(availablePeers); // Elegimos peers aleatoriamente

        for (String fragment : fragments) {
            Peer targetPeer = availablePeers.remove(0); // Peer que recibirá el fragmento
            System.out.println("Replicando fragmento '" + fragment + "' en peer " + targetPeer.getIp());
            // Simulación: agregar fragmento a la lista de archivos del peer

            // ----------------------------------
            // Conexión con Peer (gRPC para replicar)
            // ----------------------------------

        }
    }

    // // Búsqueda de un archivo
    // public List<Peer> searchFile(String fileName) {
    // lock.lock();
    // try {
    // // Retorna la lista de peers que poseen el archivo

    // // ----------------------------------
    // // Conexión con Peer (gRPC para buscar archivos)
    // // ----------------------------------

    // return fileToPeersMap.getOrDefault(fileName, new ArrayList<>());
    // } finally {
    // lock.unlock();
    // }
    // }

    // // Búsqueda de un archivo o sus fragmentos
    // public List<Peer> searchFile(String fileName) {
    // lock.lock();
    // try {
    // List<Peer> resultPeers = new ArrayList<>();

    // // Buscar el archivo exacto
    // if (fileToPeersMap.containsKey(fileName)) {
    // resultPeers.addAll(fileToPeersMap.get(fileName));
    // }

    // // Buscar archivos que empiezan con el nombre base del archivo (fragmentos)
    // for (String key : fileToPeersMap.keySet()) {
    // if (key.startsWith(fileName)) {
    // resultPeers.addAll(fileToPeersMap.get(key));
    // }
    // }

    // // Eliminar duplicados en caso de que un mismo peer esté en varios fragmentos
    // Set<Peer> uniquePeers = new HashSet<>(resultPeers);
    // return new ArrayList<>(uniquePeers);
    // } finally {
    // lock.unlock();
    // }
    // }

    // Búsqueda de un archivo o sus fragmentos
    public List<Peer> searchFile(String fileName) {
        lock.lock();
        try {
            List<Peer> resultPeers = new ArrayList<>();
            boolean foundExactFile = false;

            // Buscar el archivo exacto
            if (fileToPeersMap.containsKey(fileName)) {
                foundExactFile = true;
                List<Peer> exactFilePeers = fileToPeersMap.get(fileName);
                resultPeers.addAll(exactFilePeers);

                // Imprimir información de los peers que tienen el archivo exacto
                System.out.println("Archivo exacto '" + fileName + "' encontrado en los siguientes peers:");
                for (Peer peer : exactFilePeers) {
                    System.out.println("Peer IP: " + peer.getIp());
                }

                // ----------------------------------
                // Conexión con Peer (gRPC para retorno de info)
                // ----------------------------------

            }

            // Si no encontramos el archivo exacto, buscar fragmentos
            if (!foundExactFile) {
                for (String key : fileToPeersMap.keySet()) {
                    if (key.startsWith(fileName)) {
                        resultPeers.addAll(fileToPeersMap.get(key));
                    }
                }

                // Eliminar duplicados en caso de que un mismo peer esté en varios fragmentos
                Set<Peer> uniquePeers = new HashSet<>(resultPeers);
                resultPeers = new ArrayList<>(uniquePeers);

                // ----------------------------------
                // Conexión con Peer (gRPC para retorno de info)
                // ----------------------------------

                // Imprimir información de los peers que tienen fragmentos del archivo
                System.out.println("Archivo '" + fileName
                        + "' no encontrado exactamente. Fragmentos encontrados en los siguientes peers:");
                for (Peer peer : resultPeers) {
                    // ----------------------------------
                    // Conexión con Peer (gRPC para cambio por anotar todos los frags)
                    // ----------------------------------
                    System.out.println("Fragmento en Peer IP: " + peer.getIp());
                }
            }

            return resultPeers;
        } finally {
            lock.unlock();
        }
    }

    // Eliminar un peer de la red y borrar sus archivos
    public void unregisterPeer(Peer peer) {
        lock.lock();
        try {
            peerList.remove(peer);
            // Eliminar archivos de este peer en fileToPeersMap
            Iterator<Map.Entry<String, List<Peer>>> iterator = fileToPeersMap.entrySet().iterator();
            while (iterator.hasNext()) {
                Map.Entry<String, List<Peer>> entry = iterator.next();
                entry.getValue().remove(peer);
                if (entry.getValue().isEmpty()) {
                    iterator.remove();
                }
            }
            System.out.println("Peer " + peer.getIp() + " eliminado de la red.");

            // ----------------------------------
            // Conexión con Peer (gRPC para desconectar)
            // ----------------------------------

        } finally {
            lock.unlock();
        }
    }
}

class TrackerThread extends Thread {
    // Manejo de 2 tipos de solicitudes

    private Tracker tracker;
    private String requestType;
    private Peer peer;
    private String fileName;

    // Tipo Registro
    public TrackerThread(Tracker tracker, String requestType, Peer peer) {
        this.tracker = tracker;
        this.requestType = requestType;
        this.peer = peer;
    }

    // Tipo Búsqueda
    public TrackerThread(Tracker tracker, String requestType, String fileName) {
        this.tracker = tracker;
        this.requestType = requestType;
        this.fileName = fileName;
    }

    @Override
    public void run() {
        if (requestType.equals("register")) {
            tracker.registerPeer(peer);

            // ----------------------------------
            // Conexión con Peer (gRPC para registrar)
            // ----------------------------------

        } else if (requestType.equals("search")) {
            List<Peer> peers = tracker.searchFile(fileName);

            // ----------------------------------
            // Conexión con Peer (gRPC para buscar archivos)
            // ----------------------------------

            if (!peers.isEmpty()) {
                System.out.println("Peers que tienen el archivo " + fileName + ":");
                for (Peer p : peers) {
                    System.out.println("Peer IP: " + p.getIp());
                }
            } else {
                System.out.println("No se encontraron peers con el archivo " + fileName);
            }
        } else if (requestType.equals("unregister")) {
            tracker.unregisterPeer(peer);

            // ----------------------------------
            // Conexión con Peer (gRPC para desconectar)
            // ----------------------------------

        }
    }
}

public class TrackerApp {
    public static void main(String[] args) {
        Tracker tracker = new Tracker();

        // Peer 1: carga "file1.mp4" con tamaño 150MB (se fragmentará) y "file2.mp4" con
        // tamaño 80MB (no se fragmentará)
        Peer peer1 = new Peer("192.168.1.2", Map.of(
                "file1.mp4", 150, // Este archivo se fragmentará
                "file2.mp4", 80 // Este archivo no se fragmentará
        ));

        // Peer 2: vacío (sin archivos)
        Peer peer2 = new Peer("192.168.1.3", new HashMap<>());

        // Registrar los peers en la red
        TrackerThread registerPeer1 = new TrackerThread(tracker, "register", peer1);
        TrackerThread registerPeer2 = new TrackerThread(tracker, "register", peer2);

        registerPeer1.start();
        registerPeer2.start();

        try {
            registerPeer1.join();
            registerPeer2.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        // Imprimir archivos en los peers después del registro
        System.out.println("Archivos en Peer 1 después del registro: " + peer1.getFiles());
        System.out.println("Archivos en Peer 2 después del registro: " + peer2.getFiles());

        // Simular búsqueda de archivos
        System.out.println("Búsqueda de 'file1.mp4':");
        TrackerThread searchFile1 = new TrackerThread(tracker, "search", "file1.mp4");
        searchFile1.start();

        System.out.println("Búsqueda de 'file2.mp4':");
        TrackerThread searchFile2 = new TrackerThread(tracker, "search", "file2.mp4");
        searchFile2.start();

        try {
            searchFile1.join();
            searchFile2.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}