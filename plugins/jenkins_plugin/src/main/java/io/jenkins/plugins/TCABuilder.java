// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

package io.jenkins.plugins;

import edu.umd.cs.findbugs.annotations.NonNull;
import hudson.EnvVars;
import hudson.Extension;
import hudson.FilePath;
import hudson.Launcher;
import hudson.model.AbstractProject;
import hudson.model.Run;
import hudson.model.TaskListener;
import hudson.tasks.BuildStepDescriptor;
import hudson.tasks.Builder;
import hudson.util.FormValidation;
import jenkins.tasks.SimpleBuildStep;
import org.apache.commons.lang.StringUtils;
import org.jenkinsci.Symbol;
import org.json.JSONObject;
import org.kohsuke.stapler.DataBoundConstructor;
import org.kohsuke.stapler.DataBoundSetter;
import org.kohsuke.stapler.QueryParameter;

import javax.servlet.ServletException;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Objects;
import java.util.Properties;

public class TCABuilder extends Builder implements SimpleBuildStep {
    private final String token;
    private final String languageType;
    private final String teamId;
    private final String projectName;
    private final String branchName;
    private String codeAnalysisPath;
    private boolean total;
    public String isTotal;
    public String language;
    public String branch;
    private String osName;
    private final String refSchemeID;
    private final String scanPlan;

    private final String  threshold;

    @DataBoundConstructor
    public TCABuilder(String codeAnalysisPath,
                      String token,
                      String branchName,
                      String languageType,
                      String teamId,
                      String projectName,
                      String refSchemeID,
                      String scanPlan,
                      String threshold) {
        this.codeAnalysisPath = codeAnalysisPath;
        this.token = token;
        this.branchName = branchName;
        this.languageType = languageType;
        this.teamId = teamId;
        this.projectName = projectName;
        this.refSchemeID = refSchemeID;
        this.scanPlan = scanPlan;
        this.threshold = threshold;
    }
    public String getCodeAnalysisPath() {
        return codeAnalysisPath;
    }

    public String getToken() {
        return token;
    }

    public String getBranchName() {
        return branchName;
    }

    public String getLanguageType() {
        return languageType;
    }

    public String getTeamId(){
        return teamId;
    }

    public String getProjectName() {
        return projectName;
    }

    public boolean isTotal() {
        return total;
    }

    public String getRefSchemeID(){
        return refSchemeID;
    }

    public String getScanPlan(){
        return scanPlan;
    }

    @DataBoundSetter
    public void setTotal(boolean total) {
        this.total = total;
    }

    public String getThreshold() { return threshold; }

    @Override
    public void perform(@NonNull Run<?, ?> run, @NonNull FilePath workspace, @NonNull EnvVars env,
                        @NonNull Launcher launcher, @NonNull TaskListener listener) throws IOException {
        try {
            Properties props = System.getProperties();
            String[] osNameArray = props.getProperty("os.name").split(" ");
            osName = osNameArray[0];
        } catch (Exception ignored) {
            listener.getLogger().println("获取操作系统失败");
        }

        String localCodePath = env.get("WORKSPACE");
        String checkout_dir = env.get("GIT_CHECKOUT_DIR");
        if (StringUtils.isNotBlank(checkout_dir)){
            localCodePath += "/" + checkout_dir;
        }

        if(StringUtils.isNotBlank(codeAnalysisPath)){
            if(!codeAnalysisPath.startsWith("/")){
                codeAnalysisPath = "/" + codeAnalysisPath;
            }
            if(!codeAnalysisPath.endsWith("/")){
                codeAnalysisPath = codeAnalysisPath + "/";
            }
        }

        if(StringUtils.isNotBlank(languageType)){
            language = " --language " + languageType;
        }else{
            language = "";
        }

        if(StringUtils.isNotBlank(branchName)){
            branch = " --branch " + branchName;
        }else{
            branch = "";
        }

        if(total) {
            isTotal = " --total";
        }else{
            isTotal = "";
        }

        String constant_refSchemeID = " --ref-scheme-id ";
        if(refSchemeID != null && refSchemeID.length() != 0){
            constant_refSchemeID = constant_refSchemeID + refSchemeID;
        }else{
            constant_refSchemeID = "";
        }

        String constant_scanPlan = " --scan-plan ";
        if(scanPlan != null && scanPlan.length() != 0){
            constant_scanPlan = constant_scanPlan + scanPlan;
        }else{
            constant_scanPlan = "";
        }

        String clientPath = codeAnalysisPath + "client";
        StartClient.startClient(osName,
                                clientPath,
                                token,
                                teamId,
                                projectName,
                                localCodePath,
                                branch,
                                language,
                                isTotal,
                                constant_refSchemeID,
                                constant_scanPlan,
                                listener,
                                env);
        String fileName = clientPath + "/scan_status.json";
        String jsonStr = ReadJsonFile.readJsonFile(fileName);

        // 如果设置了质量门禁，判断结果是否符合
        if (StringUtils.isNotBlank(threshold)){
            String tca_status = "success";
            assert jsonStr != null;
            JSONObject jsonObj = new JSONObject(jsonStr);
            String status = jsonObj.getString("status");
            if(Objects.equals(status, "success")){
                JSONObject scan_report = jsonObj.getJSONObject("scan_report");
                JSONObject lintscan = scan_report.getJSONObject("lintscan");
                JSONObject total = lintscan.getJSONObject("total");
                JSONObject state_detail = total.getJSONObject("state_detail");
                int total_active_issues = state_detail.getInt("active");
                if (total_active_issues > Integer.parseInt(threshold)){
                    tca_status = "failure";
                    jsonObj.put("status", tca_status);
                    int error_code = 255;
                    jsonObj.put("error_code", error_code);
                    String msg = "扫描不通过! 问题量: " + total_active_issues + " , 超过质量门禁限制(" + threshold + ")";
                    jsonObj.put("text", msg);
                    jsonStr = jsonObj.toString(2);
                    listener.getLogger().println("质量红线: " + msg);
                }else{
                    String msg = "扫描通过! 问题量: " + total_active_issues + " , 满足质量门禁限制(" + threshold + ")";
                    jsonObj.put("text", msg);
                    jsonStr = jsonObj.toString(2);
                    listener.getLogger().println("质量红线: " + msg);
                }
            }
            // 将门禁结果状态（success|failure）写入到工作空间目录下的txt文件中，方便后续步骤进行门禁判断
            try {
                String filepath = localCodePath + "/tca_threshold.txt";
                BufferedWriter out = new BufferedWriter(new FileWriter(filepath));
                out.write(tca_status);
                out.close();
                listener.getLogger().println("质量门禁结果已写入文件: " + filepath);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        run.addAction(new ViewReportAction(jsonStr));
    }

    @Extension
    @Symbol("TCA")
    public static final class DescriptorImpl extends BuildStepDescriptor<Builder> {
        public FormValidation doCheckCodeAnalysisPath(@QueryParameter String value) throws IOException, ServletException {
            if (StringUtils.isBlank(value)){
                return FormValidation.error("必填，CodeAnalysisPath绝对路径");
            }
            return FormValidation.ok();
        }

        public FormValidation doCheckToken(@QueryParameter String value) throws IOException, ServletException {
            if (StringUtils.isBlank(value)){
                return FormValidation.error("必填，token");
            }
            return FormValidation.ok();
        }

        public FormValidation doCheckTeamId(@QueryParameter String value) throws IOException, ServletException {
            if (StringUtils.isBlank(value)){
                return FormValidation.error("必填，团队ID");
            }
            return FormValidation.ok();
        }

        public FormValidation doCheckProjectName(@QueryParameter String value) throws IOException, ServletException {
            if (StringUtils.isBlank(value)){
                return FormValidation.error("必填，项目名称");
            }
            return FormValidation.ok();
        }

        public FormValidation doCheckBranchName(@QueryParameter String value) throws IOException, ServletException {
            if (StringUtils.isBlank(value)){
                return FormValidation.warning("选填，需要扫描的分支名；如拉取代码时未指定分支，则该选项为必填");
            }
            return FormValidation.ok();
        }

        public FormValidation doCheckLanguageType(@QueryParameter String value) throws IOException, ServletException {
            if (StringUtils.isBlank(value)){
                return FormValidation.warning("选填，指定扫描的语言");
            }
            return FormValidation.ok();
        }

        public FormValidation doCheckRefSchemeID(@QueryParameter String value) throws IOException, ServletException {
            if (StringUtils.isBlank(value)){
                return FormValidation.warning("选填，分析方案模版ID");
            }
            return FormValidation.ok();
        }

        public FormValidation doCheckScanPlan(@QueryParameter String value) throws IOException, ServletException {
            if (StringUtils.isBlank(value)){
                return FormValidation.warning("选填，扫描方案名称");
            }
            return FormValidation.ok();
        }

        public FormValidation doCheckTotal(@QueryParameter boolean value) throws IOException, ServletException {
            if (!value){
                return FormValidation.ok("不勾选，默认为增量扫描");
            }
            return FormValidation.ok();
        }

        public FormValidation doCheckThreshold(@QueryParameter String value) throws IOException, ServletException {
            if (StringUtils.isBlank(value)){
                return FormValidation.warning("选填，质量门禁，填一个整数，问题量大于该值时，结果状态设置为失败，可在后续增加判断步骤终止流水线");
            }
            return FormValidation.ok();
        }

        @Override
        public String getDisplayName() {
            return "TCA";
        }

        @Override
        public boolean isApplicable(Class<? extends AbstractProject> aClass) {
            return true;
        }
    }
} 
