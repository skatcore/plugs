package com.wat;

import org.json.JSONObject;

class PlugDTO {
    private int houseCode;
    private int id;
    private String name;
    private int status;

    PlugDTO(int houseCode, int id, String name, int status) {
        this.houseCode = houseCode;
        this.id = id;
        this.name = name;
        this.status = status;
    }

    int getHouseCode() {
        return houseCode;
    }

    int getId() {
        return id;
    }

    JSONObject toJson() {
        JSONObject res = new JSONObject();
        res.put("houseCode", houseCode);
        res.put("id", id);
        res.put("name", name);
        res.put("status", status);

        return res;
    }
}
