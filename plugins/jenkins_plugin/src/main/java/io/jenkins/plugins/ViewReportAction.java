// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

package io.jenkins.plugins;
import hudson.model.Run;
import jenkins.model.RunAction2;

public class ViewReportAction implements RunAction2 {
    private final String jsonStr;
    private transient Run run;

    public ViewReportAction(String jsonStr){
        this.jsonStr = jsonStr;
    }
    public String getJsonStr() {
        return jsonStr;
    }
    public Run getRun() {
        return run;
    }
    @Override
    public String getIconFileName() {
        return "document.png";
    }
    @Override
    public String getDisplayName() {
        return "代码分析报告";
    }
    @Override
    public String getUrlName() {
        return "report";
    }
    @Override
    public void onAttached(Run<?, ?> run) {
        this.run = run;
    }
    @Override
    public void onLoad(Run<?, ?> run) {
        this.run = run;
    }
}
