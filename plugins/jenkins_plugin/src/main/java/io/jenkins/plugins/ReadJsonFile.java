// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

package io.jenkins.plugins;
import java.io.*;
import java.nio.charset.StandardCharsets;

public class ReadJsonFile {
    public static String readJsonFile(String clientPath){
        String jsonStr;
        try {
            File jsonFile = new File(clientPath);
            FileReader fileReader = new FileReader(jsonFile);
            Reader reader = new InputStreamReader(
                    new FileInputStream(jsonFile),
                    StandardCharsets.UTF_8);
            int ch;
            StringBuilder sb = new StringBuilder();
            while ((ch = reader.read()) != -1) {
                sb.append((char) ch);
            }
            fileReader.close();
            reader.close();
            jsonStr = sb.toString();
            return jsonStr;
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }
}
