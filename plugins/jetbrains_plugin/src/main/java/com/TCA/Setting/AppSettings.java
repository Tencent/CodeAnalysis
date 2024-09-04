package com.TCA.Setting;

import com.intellij.openapi.components.PersistentStateComponent;
import com.intellij.openapi.components.State;
import com.intellij.openapi.components.Storage;
import com.intellij.openapi.application.ApplicationManager;
import org.jetbrains.annotations.NotNull;

@State(
        name = "org.intellij.sdk.settings.AppSettings",
        storages = @Storage("SdkSettingsPlugin.xml")
)
//此类是用于持久化存储用户输入的设置参数的服务类, 已在配置文件中注册
public final class AppSettings implements PersistentStateComponent<AppSettings.State> {

    public static class State {
        //去除python3的python安装路径
        public String pythonPath = "";
        //完整的python3安装路径
        public String ePythonPath;
        //TCA源码路径
        public String codeAnalysisPath = "";
        //TCA源码下client目录的绝对路径
        public String codeAnalysisClientPath;
        //个人token
        public String token = "";
        //分析方案模板ID
        public String schemeTemplateId = "";
        //团队唯一标识
        public String orgSid = "";
        //要分析的项目路径, 右键时会更新此参数, 在执行 重新运行上一次目录或文件分析 时会用到此参数
        public String sourceDir = "";
        //指定要分析的文件
        public String file = "";
    }

    private State myState = new State();

    public static AppSettings getInstance() {
        return ApplicationManager.getApplication().getService(AppSettings.class);
    }

    @Override
    public State getState() {
        return myState;
    }

    @Override
    public void loadState(@NotNull State state) {
        myState = state;
    }
}
