package com.TCA.Setting;

import com.intellij.ui.components.JBLabel;
import com.intellij.ui.components.JBTextField;
import com.intellij.util.ui.FormBuilder;
import org.jetbrains.annotations.NotNull;

import javax.swing.*;

//创建设置页面的类, 被AppSettingsConfigurable调用
public class AppSettingsComponent {
    //定义输入框
    private final JPanel myMainPanel;
    private final JBTextField ePythonPath = new JBTextField();
    private final JBTextField codeAnalysisPath = new JBTextField();
    private final JBTextField token = new JBTextField();
    private final JBTextField schemeTemplateId = new JBTextField();
    private final JBTextField orgSid = new JBTextField();

    //创建页面实例
    public AppSettingsComponent() {
        myMainPanel = FormBuilder.createFormBuilder()
                .addLabeledComponent(new JBLabel("Python3安装路径(python3版本应为3.7):"), ePythonPath, false)
                .addComponent(new JBLabel())
                .addLabeledComponent(new JBLabel("TCA源码安装路径(以CodeAnalysis目录结束):"), codeAnalysisPath, false)
                .addComponent(new JBLabel())
                .addLabeledComponent(new JBLabel("个人Token(从TCA的个人中心获取):"), token, false)
                .addComponent(new JBLabel())
                .addLabeledComponent(new JBLabel("分析方案模版ID(TCA中创建方案并获取):"), schemeTemplateId, false)
                .addComponent(new JBLabel())
                .addLabeledComponent(new JBLabel("团队唯一标识(TCA中创建团队并获取):"), orgSid, false)
                .addComponent(new JBLabel())
                .addComponentFillVertically(new JPanel(), 1)
                .getPanel();
    }

    //获取设置界面
    public JPanel getPanel() {
        return myMainPanel;
    }

    //get方法获取用户输入,set方法更新设置页显示的数据
    @NotNull
    public String getePythonPath() {
        return ePythonPath.getText();
    }

    public void setePythonPath(@NotNull String pythonPath) {
        this.ePythonPath.setText(pythonPath);
    }

    @NotNull
    public String getCodeAnalysisPath() {
        return codeAnalysisPath.getText();
    }

    public void setCodeAnalysisPath(@NotNull String codeAnalysisPath) {
        this.codeAnalysisPath.setText(codeAnalysisPath);
    }

    @NotNull
    public String getToken() {
        return token.getText();
    }

    public void setToken(@NotNull String token) {
        this.token.setText(token);
    }

    @NotNull
    public String getSchemeTemplateId() {
        return schemeTemplateId.getText();
    }

    public void setSchemeTemplateId(@NotNull String schemeTemplateId) {
        this.schemeTemplateId.setText(schemeTemplateId);
    }

    @NotNull
    public String getOrgSid() {
        return orgSid.getText();
    }

    public void setOrgSid(@NotNull String orgSid) {
        this.orgSid.setText(orgSid);
    }

}