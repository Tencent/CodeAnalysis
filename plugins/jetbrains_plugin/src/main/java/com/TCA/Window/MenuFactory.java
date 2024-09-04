package com.TCA.Window;

import com.intellij.openapi.project.DumbAware;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.wm.ToolWindow;
import com.intellij.openapi.wm.ToolWindowFactory;
import com.intellij.ui.content.Content;
import com.intellij.ui.content.ContentFactory;
import org.jetbrains.annotations.NotNull;

//窗口工厂类, 此类在配置文件中注册, 用于实现在idea底部添加窗口
public class MenuFactory implements ToolWindowFactory, DumbAware {

    //实现接口方法来设置页面样式
    @Override
    public void createToolWindowContent(@NotNull Project project, @NotNull ToolWindow toolWindow) {
        //创建ProjectMenu实例
        ProjectMenu projectMenu = new ProjectMenu();
        ContentFactory contentFactory = ContentFactory.getInstance();
        //使用ProjectMenu实例作为一个标签页
        Content proContent = contentFactory.createContent(projectMenu.createMenu(project), "本地代码分析", false);
        toolWindow.getContentManager().addContent(proContent);
    }
}