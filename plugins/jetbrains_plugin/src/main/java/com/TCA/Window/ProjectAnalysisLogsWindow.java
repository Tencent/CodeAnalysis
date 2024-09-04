package com.TCA.Window;

import com.TCA.Action.*;
import com.intellij.openapi.actionSystem.ActionManager;
import com.intellij.openapi.actionSystem.ActionToolbar;
import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.DefaultActionGroup;
import com.intellij.openapi.project.Project;
import com.intellij.ui.JBColor;
import com.intellij.ui.components.JBScrollPane;

import javax.swing.*;
import javax.swing.text.BadLocationException;
import javax.swing.text.Style;
import javax.swing.text.StyleConstants;
import javax.swing.text.StyledDocument;
import java.awt.*;
import java.util.HashMap;
import java.util.Map;

//此类用于创建分析日志标签页
public class ProjectAnalysisLogsWindow {
    //定义分析日志标签页map, 为每一个打开的项目创建一个分析日志标签页
    private static final Map<String, JPanel> windows = new HashMap<>();
    //定义分析日志文本域map, 为每一个打开的项目创建一个文本域
    private static final Map<String, JTextPane> textPanes = new HashMap<>();

    private ProjectAnalysisLogsWindow(Project project) {
        //初始化分析日志标签页
        JPanel window = new JPanel(new BorderLayout());
        //定义动作组
        DefaultActionGroup actionGroup = new DefaultActionGroup();
        //添加 重新执行上一次目录或文件分析 动作到动作组
        AnAction restart = new RestartLastAnalysis();
        actionGroup.add(restart);
        //添加 工程分析 动作到动作组
        AnAction run = new StartProjectAnalysis();
        actionGroup.add(run);
        //添加 清除日志 动作到动作组
        AnAction clearLogs = new ClearLogs();
        actionGroup.add(clearLogs);
        //使用动作组创建工具栏
        ActionToolbar actionToolbar = ActionManager.getInstance().createActionToolbar("ProjectAnalysisWindowToolbar", actionGroup, false);
        actionToolbar.setTargetComponent(window);

        //将工具栏添加到分析日志标签页的左侧
        window.add(actionToolbar.getComponent(), BorderLayout.WEST);

        //初始化文本域
        JTextPane textPane = new JTextPane();
        //设置不可编辑
        textPane.setEditable(false);
        //添加文本域到分析滚动条
        JBScrollPane jScrollPane = new JBScrollPane(textPane,
                JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
                JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);
        //添加滚动条分析日志标签页
        window.add(jScrollPane, BorderLayout.CENTER);

        windows.put(project.getBasePath(), window);
        textPanes.put(project.getBasePath(), textPane);
    }

    public static JComponent getContent(Project project) {
        //保证每个打开的项目只会创建一个分析日志标签页, 因为更新文本域时需要获取到项目的JTextPane实例, 然后修改其内容, 所以要用单例模式(这里单例获取window修改内容也可以)
        //为每个项目创建一个标签页可以防止在打开多个项目的时候出现问题
        if(!windows.containsKey(project.getBasePath()))
            new ProjectAnalysisLogsWindow(project);
        return windows.get(project.getBasePath());
    }

    //追加文本到分析日志标签页的文本域中
    public static void addText(String msg, String projectPath) {
        StyledDocument styledDocument = textPanes.get(projectPath).getStyledDocument();
        Style style = textPanes.get(projectPath).addStyle("CustomStyle", null);

        // 大小
        StyleConstants.setFontSize(style, 13);
        // 字体
        StyleConstants.setFontFamily(style, "JetBrains Mono");
        // 颜色
        StyleConstants.setForeground(style, JBColor.GREEN);

        try {
            styledDocument.insertString(styledDocument.getLength(), msg + '\n', style);
            textPanes.get(projectPath).setCaretPosition(styledDocument.getLength());
        } catch (BadLocationException e) {
            throw new RuntimeException(e);
        }
    }

    //清除分析日志标签页中的日志
    public static void clearLogs(String projectPath) {
        textPanes.get(projectPath).setText("");
    }
}