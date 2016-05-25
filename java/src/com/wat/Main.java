package com.wat;

/*import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
*/

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;


public class Main {
    private static final int PORT = 5432;

    private static DataInputStream in;
    private static DataOutputStream out;

    public static void main(String[] args) throws IOException {
        System.out.println("Server gestartet.");

        System.out.println("Server beendet.");

        /*
        ServerSocket serverSocket = new ServerSocket(PORT);
        log("Server: " + InetAddress.getLocalHost());
        log("Listening at port " +PORT +".");

        while(true) {
            log("Waiting for client to connect...");
            Socket clientSocket = serverSocket.accept();
            log("Client connected!");
            in = new DataInputStream(clientSocket.getInputStream());
            out = new DataOutputStream(clientSocket.getOutputStream());

            try {
                while (true) {
                    log("Waiting for data (JSON).");
                    String s = in.readUTF();

                    try {
                        JSONObject json = new JSONObject(s);
                        log("Successfully received json: " +json.toString());
                        processJSON(json);
                    } catch (JSONException e) {
                        e.printStackTrace();
                        log("Received bad JSON format: " + s);
                        System.exit(-42);
                    }
                }
            } catch (EOFException e) {
                log("Client disconnected.");
            } catch (Exception e) {
                log("Unknown error, drop client.");
            }
        }*/
    }
/*
    private static void processJSON(JSONObject jsonRecv) throws JSONException, IOException {

        switch (jsonRecv.getInt("type")) {
            case 0:
                sendMatchStatus();
                break;
            case 1:
                break;
        }
    }


    private static void sendMatchStatus() throws JSONException, IOException {
        JSONObject res = new JSONObject();

        res.put("type", 42);
        res.put("status", 1); // Match running.
        JSONArray jsonArray = new JSONArray();
        final String[] names = {"Yolo", "Swag", "Lol", "Obey"};
        for (String s : names) {
            JSONObject jsonName = new JSONObject();
            jsonName.put("name", s);
            jsonArray.put(jsonName);
        }
        res.put("names", jsonArray);
        res.put("starttime", 42);

        res.put("goalcountblue", 2);
        JSONArray goalsBlue = new JSONArray();
        JSONObject goalBlue1 = new JSONObject();
        goalBlue1.put("timestamp", 44);
        JSONObject goalBlue2 = new JSONObject();
        goalBlue2.put("timestamp", 500);
        goalsBlue.put(goalBlue1);
        goalsBlue.put(goalBlue2);
        res.put("timestampsblue", goalsBlue);

        res.put("goalcountred", 1);
        JSONArray goalsRed = new JSONArray();
        JSONObject goalRed1 = new JSONObject();
        goalRed1.put("timestamp", 255);
        goalsRed.put(goalRed1);
        res.put("timestampsred", goalsRed);

        sendJson(res);
    }

    private static void sendJson(JSONObject json) throws IOException {
        log("Send JSON: " +json.toString());
        out.writeUTF(json.toString());
        out.flush();
    }

    private static void log(String s) {
        System.out.println(s);
    }
*/
}
