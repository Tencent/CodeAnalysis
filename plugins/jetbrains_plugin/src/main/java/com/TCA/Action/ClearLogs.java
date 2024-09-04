package com.TCA.Action;

import com.TCA.Window.ProjectAnalysisLogsWindow;
import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.util.IconLoader;
import org.jetbrains.annotations.NotNull;

//继承AnAction类, 为动作类
public class ClearLogs extends AnAction {

    public ClearLogs() {
        // 设置动作的名称和图标，在工具栏或菜单中显示
        super("清除日志", "", IconLoader.getIcon("/icons/clearLogs.svg", ClearLogs.class));
    }

    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {
        //清除日志功能
        ProjectAnalysisLogsWindow.clearLogs(e.getProject().getBasePath());
    }
}
