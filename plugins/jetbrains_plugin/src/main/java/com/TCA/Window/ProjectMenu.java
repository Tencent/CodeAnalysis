package com.TCA.Window;

import com.intellij.openapi.project.Project;
import com.intellij.ui.components.JBTabbedPane;

import javax.swing.*;
import java.awt.*;
//此类用于创建本地代码分析标签页
public class ProjectMenu {

    public JBTabbedPane createMenu(Project project) {

        //创建JBTabbedPane实例, JBTabbedPane可以包含多个标签页
        JBTabbedPane tabbedPane = new JBTabbedPane();

        //获取两个页面实例
        JPanel panel1 = new JPanel(new BorderLayout());
        panel1.add(ProjectAnalysisLogsWindow.getContent(project));

        JPanel panel2 = new JPanel(new BorderLayout());
        panel2.add(ProjectAnalysisDataWindow.getContent(project));

        // 将这些页面实例作为选项卡添加到 JBTabbedPane
        tabbedPane.addTab("分析日志", panel1);
        tabbedPane.addTab("分析结果", panel2);

        return tabbedPane;
    }
}
