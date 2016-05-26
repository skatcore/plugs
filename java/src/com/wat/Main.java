package com.wat;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.*;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Enumeration;


public class Main {
    private static final int PORT = 5432;
    private static final String EXEC_FILE = "~plugs/Assignment-4/plug";
    private static final String SPACE = " ";
    private static DataOutputStream out;

    private static ArrayList<PlugDTO> plugs = new ArrayList<>();

    public static void main(String[] args) throws IOException {
        log("Server started.");

        //setPlug(42, 20, 1);


        NetworkInterface nif = NetworkInterface.getByName("wlan0");
        Enumeration<InetAddress> nifAddresses = nif.getInetAddresses();

        log("Address: " + nifAddresses.nextElement().toString());

        InetAddress inetAddress = nifAddresses.nextElement();
        ServerSocket serverSocket = new ServerSocket(PORT, 20, inetAddress);

        log("Server: " + InetAddress.getLocalHost());
        log("Listening at port " +PORT +".");

        //noinspection InfiniteLoopStatement
        while(true) {
            log("Waiting for client to connect...");
            Socket clientSocket = serverSocket.accept();
            log("Client connected!");
            DataInputStream in = new DataInputStream(clientSocket.getInputStream());
            out = new DataOutputStream(clientSocket.getOutputStream());

            try {
                //noinspection InfiniteLoopStatement
                while (true) {
                    log("Waiting for data (JSON).");
                    String s = in.readUTF();

                    try {
                        JSONObject json = new JSONObject(s);
                        log("Successfully received json: " +json.toString());
                        processJSON(json);
                    } catch (JSONException e) {
                        log("Received bad JSON format, ignoring: " + s);
                    }
                }
            } catch (EOFException e) {
                log("Client disconnected.");
            } catch (Exception e) {
                log("Unknown error, drop client.");
            }
        }
    }

    /**
     * Sets the given plug to the given status by calling a C executable.
     *
     * @param houseCode The house code.
     * @param id        The id.
     * @param status    The status, 0 or 1.
     */
    private static void setPlug(int houseCode, int id, int status) {
        String s;
        Process p;
        try {
            final String command = EXEC_FILE + SPACE + houseCode + SPACE + id + SPACE + status; // e.g. ./plugs 31 42 1 or ./plugs 31 42 0
            System.out.println("Executing: " + command);
            p = Runtime.getRuntime().exec(command);

            BufferedReader br = new BufferedReader(
                    new InputStreamReader(p.getInputStream()));
            while ((s = br.readLine()) != null)
                System.out.println("line: " + s);
            p.waitFor();
            System.out.println("exit: " + p.exitValue());
            p.destroy();
        } catch (InterruptedException | IOException e) {
            e.printStackTrace();
        }
    }

    private static void processJSON(JSONObject json) throws IOException, InterruptedException {
        int houseCode;
        int id;
        int status;
        String name;

        switch (json.getString("type")) {
            case "getPlugs":
                // No data expected.
                sendPlugList();
                break;

            case "addOrUpdatePlug":
                houseCode = json.getInt("houseCode");
                id = json.getInt("id");
                name = json.getString("name");
                if (json.has("status")) {
                    status = json.getInt("status");
                } else {
                    status = 0;
                }

                addOrUpdatePlug(houseCode, id, name, status);
                break;

            case "removePlug":
                houseCode = json.getInt("houseCode");
                id = json.getInt("id");

                removePlug(houseCode, id);
                break;

            case "setPlug":
                houseCode = json.getInt("houseCode");
                id = json.getInt("id");
                status = json.getInt("status");

                // Call several times to be more reliable.
                for (int i = 0; i < 4; i++) {
                    setPlug(houseCode, id, status);
                    Thread.sleep(250);
                }
                break;
        }
    }

    /**
     * Searches for the given plug.
     *
     * @param houseCode The house code.
     * @param id        The id.
     * @return The index in plugs list, or -1 if not present in list.
     */
    private static int getPlugIndex(int houseCode, int id) {
        for (int i = 0; i < plugs.size(); i++) {
            final PlugDTO plug = plugs.get(i);
            if (plug.getHouseCode() == houseCode && plug.getId() == id) {
                return i; // Plug found.
            }
        }
        return -1; // Plug not in list.
    }

    /**
     * Removes the given plug, if present.
     *
     * @param houseCode The house code.
     * @param id        The id.
     */
    private static void removePlug(int houseCode, int id) {
        final int i = getPlugIndex(houseCode, id);
        if (i != -1) {
            plugs.remove(i);
            log("Removed plug: houseCode " + houseCode + ", id " + id + ".");
        }
    }

    /**
     * Adds the given plug, or updates if present.
     *
     * @param houseCode The house code.
     * @param id        The id.
     * @param name      The name.
     * @param status    The status, 0 or 1.
     */
    private static void addOrUpdatePlug(int houseCode, int id, String name, int status) {
        final int i = getPlugIndex(houseCode, id);

        PlugDTO newPlug = new PlugDTO(houseCode, id, name, status);

        if (i == -1) {
            plugs.add(newPlug);
            log("Added plug: houseCode " + houseCode + ", id " + id + ", name " + name + ", status " + status + ".");
        } else {
            plugs.set(i, newPlug);
            log("Updated plug: houseCode " + houseCode + ", id " + id + ", name " + name + ", status " + status + ".");
        }
    }

    private static void sendPlugList() throws IOException {
        JSONObject json = new JSONObject();
        json.put("type", "getPlugs");

        JSONArray array = new JSONArray();
        for (PlugDTO plug : plugs) {
            array.put(plug.toJson());
        }
        json.put("plugs", array);
        log("Sending plug list to client.");
        sendJson(json);
    }

    private static void sendJson(JSONObject json) throws IOException {
        log("Sending JSON: " + json.toString());
        out.writeUTF(json.toString());
        out.flush();
    }

    private static void log(String s) {
        System.out.println(s);
    }

}
