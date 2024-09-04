package com.TCA.Action;

import com.TCA.Setting.AppSettings;
import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.actionSystem.CommonDataKeys;
import com.intellij.openapi.actionSystem.Presentation;
import com.intellij.openapi.util.IconLoader;
import com.intellij.openapi.vfs.VirtualFile;
import org.jetbrains.annotations.NotNull;

import java.io.File;
import java.util.Objects;

//此类是动作类, 用于实现右键启动分析的功能, 已在配置文件中注册
public class MenuSelect extends AnAction {

    //用于更新按钮的可用状态
    private static Boolean isEnable = true;

    //构造函数, 设置按钮的图标和文本
    public MenuSelect() {
        // 设置动作的名称和图标，在工具栏或菜单中显示
        super("当前路径开启TCA代码分析", "", IconLoader.getIcon("/icons/run.svg", MenuSelect.class));
    }

    //更新按钮状态, 设置按钮是否可用
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

    //此动作类的入口, 点击按钮会先执行此函数
    @Override
    public void actionPerformed(@NotNull AnActionEvent event) {
        //设置按钮不可用
        unUseButton(event);
        //获取参数设置服务的实例
        AppSettings.State state = Objects.requireNonNull(AppSettings.getInstance().getState());

        // 获取文件或目录的路径
        VirtualFile virtualFile = event.getData(CommonDataKeys.VIRTUAL_FILE);
        String filePath;
        if (virtualFile != null) {
            filePath = virtualFile.getPath();
        } else {
            filePath = event.getProject().getBasePath();
        }
        if(filePath == null) {
            System.out.println(filePath);
            return;
        }
        //存储路径到设置服务, 为重新运行上一次右键分析做准备
        state.sourceDir = filePath;
        File file = new File(filePath);

        //判断是在文件上右键还是在目录上右键
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
