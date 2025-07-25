package com.TCA.Action;

import com.TCA.Setting.AppSettings;
import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.actionSystem.Presentation;
import com.intellij.openapi.util.IconLoader;
import org.jetbrains.annotations.NotNull;

import java.io.File;
import java.util.Objects;

//此类是动作类, 用于实现重新运行上一次右键分析的功能
public class RestartLastAnalysis extends AnAction {
    private static Boolean isEnable = true;

    public RestartLastAnalysis() {
        // 设置动作的名称和图标，在工具栏或菜单中显示
        super("重新运行上一次目录或文件分析", "", IconLoader.getIcon("/icons/run.svg", MenuSelect.class));
    }

    //更新按钮状态
    @Override
    public void update(@NotNull AnActionEvent event) {
        Presentation presentation = event.getPresentation();
        presentation.setEnabled(isEnable);
    }

    //设置按钮不可用
    private void unUseButton(AnActionEvent event) {
        isEnable = false;
        update(event);
        Presentation presentation = event.getPresentation();
        presentation.setIcon(IconLoader.getIcon("/icons/canNotRun.svg", StartFileAnalysis.class));
    }

    //设置按钮可用
    private void useButton(AnActionEvent event) {
        isEnable = true;
        update(event);
        Presentation presentation = event.getPresentation();
        presentation.setIcon(IconLoader.getIcon("/icons/run.svg", StartFileAnalysis.class));
    }

    //此动作类的入口, 点击按钮执行此函数
    @Override
    public void actionPerformed(@NotNull AnActionEvent event) {
        //设置按钮不可用
        unUseButton(event);
        //获取参数设置服务的实例
        AppSettings.State state = Objects.requireNonNull(AppSettings.getInstance().getState());
        File file = new File(state.sourceDir);
        //判断file是目录还是文件, 执行对应的分析方法
        if (file.isDirectory()) {
            StartDirectoryAnalysis startDirectoryAnalysis = new StartDirectoryAnalysis();
            startDirectoryAnalysis.actionPerformed(event);

        } else {
            StartFileAnalysis startFileAnalysis = new StartFileAnalysis();
            startFileAnalysis.actionPerformed(event);
        }
        //设置按钮可用
        useButton(event);
    }
}
