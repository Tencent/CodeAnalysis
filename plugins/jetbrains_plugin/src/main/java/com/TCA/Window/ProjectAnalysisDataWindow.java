package com.TCA.Window;

import com.TCA.Action.RestartLastAnalysis;
import com.TCA.Action.StartProjectAnalysis;
import com.intellij.openapi.actionSystem.*;
import com.intellij.openapi.project.Project;
import com.intellij.ui.components.JBScrollPane;
import com.intellij.ui.treeStructure.Tree;
import kotlinx.html.S;

import javax.swing.*;
import java.awt.*;
import java.util.HashMap;
import java.util.Map;

//此类用于创建分析结果标签页
public class ProjectAnalysisDataWindow {

    //定义分析结果标签页map, 为每个打开的项目分配一个分析结果标签页
    private static final Map<String, JPanel> windows = new HashMap<>();
    //定义分析结果标签页的滚动条map, 为每个打开的项目的分析结果标签页分配一个滚动条
    private static final Map<String, JScrollPane> scrollPanes = new HashMap<>();

    private ProjectAnalysisDataWindow(Project project) {
        //初始化分析结果标签页
        JPanel window = new JPanel(new BorderLayout());
        //定义动作组
        DefaultActionGroup actionGroup = new DefaultActionGroup();
        //添加 重新执行上一次目录或文件分析 动作到动作组
        AnAction restart = new RestartLastAnalysis();
        actionGroup.add(restart);
        //添加 工程分析 动作到动作组
        AnAction run = new StartProjectAnalysis();
        actionGroup.add(run);
        //使用动作组创建工具栏
        ActionToolbar actionToolbar = ActionManager.getInstance().createActionToolbar("ProjectAnalysisWindowToolbar", actionGroup, false);
        actionToolbar.setTargetComponent(window);

        // 将工具栏添加到分析结果标签页的左侧
        window.add(actionToolbar.getComponent(), BorderLayout.WEST);

        //把滚动条添加到分析结果标签页
        JScrollPane scrollPane = new JBScrollPane();
        window.add(scrollPane, BorderLayout.CENTER);

        //把创建的window和scrollPane添加到标签页中
        windows.put(project.getBasePath(), window);
        scrollPanes.put(project.getBasePath(), scrollPane);
    }

    public static JComponent getContent(Project project) {
        //保证每个打开的项目只创建一个分析结果标签页, 因为更新结果树时需要获取到项目的JScrollPane实例, 然后修改其内容, 所以要用单例模式(这里单例获取window修改内容也可以)
        //为每个项目创建一个标签页可以防止在打开多个项目的时候出现问题
        if(!windows.containsKey(project.getBasePath()))
            new ProjectAnalysisDataWindow(project);
        return windows.get(project.getBasePath());
    }
    //设置分析结果标签页中滚动条里的结果树, 以此来达到覆盖前一次分析结果的功能
    public static void setDataTree(Tree tree, String projectPath) {
        scrollPanes.get(projectPath).setViewportView(tree);
    }
}
