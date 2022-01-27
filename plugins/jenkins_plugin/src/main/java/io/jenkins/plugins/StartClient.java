/* -*- encoding: utf-8 -*-
   Copyright (c) 2022 THL A29 Limited

   This source code file is made available under MIT License
   See LICENSE for details
   ==============================================================================
*/

package io.jenkins.plugins;
import hudson.model.TaskListener;
import java.io.*;


public class StartClient {
    public static void startClient(String osName,
                                   String clientPath,
                                   String token,
                                   String teamId,
                                   String projectName,
                                   String localCodePath,
                                   String branchName,
                                   String languageType,
                                   String isTotal,
                                   TaskListener listener) {
        
            try {
                String startCommand ="/Library/Frameworks/Python.framework/Versions/3.7/bin/python3 codepuppy.py localscan"
                        + " -t " + token
                        + " --org-sid " + teamId
                        + " --team-name " + projectName
                        + " -s " + localCodePath
                        + " --branch " + branchName
                        + " --language " + languageType
                        + isTotal;

                Process p = Runtime.getRuntime().exec(
                        startCommand,
                        new String[]{"PATH=/Library/Frameworks/Python.framework/Versions/3.7/bin:/usr/local/bin"},
                        new File(clientPath));

                final InputStream is = p.getErrorStream();

                new Thread(() -> {
                    BufferedReader br = new BufferedReader(new InputStreamReader(is));
                    try {
                        String line;
                        while ((line = br.readLine()) !=  null) {
                            listener.getLogger().println(line);
                        }
                    } catch (IOException e) {
                        e.printStackTrace();
                    } finally{
                        try {
                            is.close();
                        } catch (IOException e) {
                            listener.getLogger().println(e);
                        }
                    }
                }).start();
                p.waitFor();
            } catch (IOException | InterruptedException e) {
                listener.getLogger().println(e);
            }
        }
    }
