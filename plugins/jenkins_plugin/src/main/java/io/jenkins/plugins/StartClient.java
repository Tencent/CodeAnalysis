// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

package io.jenkins.plugins;
import hudson.EnvVars;
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
                                   String constant_refSchemeID,
                                   String constant_scanPlan,
                                   TaskListener listener,
                                   EnvVars env) {
        try {
            String PythonPath = env.get("PYTHONPATH");
            if(PythonPath == null){
                listener.getLogger().println("PYTHONPATH环境变量获取失败,请在全局变量中添加");
                System.exit(0);
            }
            if(!PythonPath.endsWith("/")){
                PythonPath = PythonPath + "/";
            }
            String GitPath = env.get("GITPATH");
            if(GitPath == null){
                listener.getLogger().println("GitPath环境变量获取失败，请在全局变量中添加");
                System.exit(0);
            }
            env.override("PATH", PythonPath + ":" + GitPath + ":" + "$PATH");

            String startCommand = PythonPath
                    + "python3 codepuppy.py localscan"
                    + " -t " + token
                    + " --org-sid " + teamId
                    + " --team-name " + projectName
                    + " -s " + localCodePath
                    + branchName
                    + languageType
                    + constant_refSchemeID
                    + constant_scanPlan
                    + isTotal;

            listener.getLogger().println("run command: " + startCommand);

            Process p = Runtime.getRuntime().exec(
                    startCommand,
                    new String[]{"PATH=" + env.get("PATH")},
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
