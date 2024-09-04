package com.TCA.Setting;

import com.intellij.openapi.options.Configurable;
import org.jetbrains.annotations.Nls;
import org.jetbrains.annotations.Nullable;

import javax.swing.*;
import java.util.Objects;

final class AppSettingsConfigurable implements Configurable {

    private AppSettingsComponent mySettingsComponent;

    @Nls(capitalization = Nls.Capitalization.Title)
    @Override
    public String getDisplayName() {
        return "TCA-分析参数配置";
    }

    @Override
    public JComponent getPreferredFocusedComponent() {
        //第一次打开设置页面时选中的组件
        return mySettingsComponent.getPanel();
    }

    @Nullable
    @Override
    public JComponent createComponent() {
        //获取设置页的实例
        mySettingsComponent = new AppSettingsComponent();
        return mySettingsComponent.getPanel();
    }

    @Override
    public boolean isModified() {
        //检查设置是否被修改,修改后用户才能选择更新设置
        AppSettings.State state = Objects.requireNonNull(AppSettings.getInstance().getState());
        return  !mySettingsComponent.getePythonPath().equals(state.ePythonPath) ||
                !mySettingsComponent.getCodeAnalysisPath().equals(state.codeAnalysisPath) ||
                !mySettingsComponent.getToken().equals(state.token) ||
                !mySettingsComponent.getSchemeTemplateId().equals(state.schemeTemplateId) ||
                !mySettingsComponent.getOrgSid().equals(state.orgSid);
    }

    @Override
    public void apply() {
        //保存设置
        AppSettings.State state = Objects.requireNonNull(AppSettings.getInstance().getState());
        state.ePythonPath = mySettingsComponent.getePythonPath();
        //减去路径中的python3
        state.pythonPath = state.ePythonPath;
        state.pythonPath = state.pythonPath.substring(0, state.pythonPath.length() - 7);

        state.codeAnalysisPath = mySettingsComponent.getCodeAnalysisPath();
        //拼接client源码路径
        state.codeAnalysisClientPath = state.codeAnalysisPath;
        if(!state.codeAnalysisClientPath.startsWith("/"))
            state.codeAnalysisClientPath = "/" + state.codeAnalysisClientPath;
        if(!state.codeAnalysisClientPath.endsWith("/"))
            state.codeAnalysisClientPath = state.codeAnalysisClientPath + "/";
        state.codeAnalysisClientPath = state.codeAnalysisClientPath + "client";

        state.token = mySettingsComponent.getToken();
        state.schemeTemplateId = mySettingsComponent.getSchemeTemplateId();
        state.orgSid = mySettingsComponent.getOrgSid();
        reset();
    }

    @Override
    public void reset() {
        //重置设置到上次保存的状态
        AppSettings.State state = Objects.requireNonNull(AppSettings.getInstance().getState());
        mySettingsComponent.setePythonPath(state.ePythonPath);
        mySettingsComponent.setCodeAnalysisPath(state.codeAnalysisPath);
        mySettingsComponent.setToken(state.token);
        mySettingsComponent.setSchemeTemplateId(state.schemeTemplateId);
        mySettingsComponent.setOrgSid(state.orgSid);
    }

    @Override
    public void disposeUIResources() {
        //释放UI资源
        mySettingsComponent = null;
    }

}