// Copyright (c) 2022 THL A29 Limited
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
import org.kohsuke.stapler.DataBoundConstructor;
import org.kohsuke.stapler.DataBoundSetter;
import org.kohsuke.stapler.QueryParameter;
import javax.servlet.ServletException;
import java.io.IOException;
import java.util.Properties;

public class TCABuilder extends Builder implements SimpleBuildStep {
    private final String token;
    private final String branchName;
    private final String languageType;
    private final String teamId;
    private final String projectName;
    private String codeAnalysisPath;
    private boolean total;
    public String isTotal;
    private String osName;
    private final String refSchemeID;
    private final String scanPlan;

    @DataBoundConstructor
    public TCABuilder(String codeAnalysisPath,
                      String token,
                      String branchName,
                      String languageType,
                      String teamId,
                      String projectName,
                      String refSchemeID,
                      String scanPlan) {
        this.codeAnalysisPath = codeAnalysisPath;
        this.token = token;
        this.branchName = branchName;
        this.languageType = languageType;
        this.teamId = teamId;
        this.projectName = projectName;
        this.refSchemeID = refSchemeID;
        this.scanPlan = scanPlan;
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

    @Override
    public void perform(@NonNull Run<?, ?> run, @NonNull FilePath workspace, @NonNull EnvVars env,
                        @NonNull Launcher launcher, @NonNull TaskListener listener) {
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
                                branchName,
                                languageType,
                                isTotal,
                constant_refSchemeID,
                constant_scanPlan,
                                listener,
                                env);
        String fileName = clientPath + "/scan_status.json";
        String jsonStr = ReadJsonFile.readJsonFile(fileName);
        run.addAction(new ViewReportAction(jsonStr));
    }

    @Extension
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
                return FormValidation.error("必填，需要扫描的分支名");
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
