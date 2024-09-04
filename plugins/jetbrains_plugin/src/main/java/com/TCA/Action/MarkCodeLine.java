package com.TCA.Action;

import com.TCA.Data.ErrorData;
import com.TCA.Data.MarkCodeMessage;
import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.editor.markup.*;
import com.intellij.openapi.fileEditor.FileEditor;
import com.intellij.openapi.fileEditor.FileEditorManager;
import com.intellij.openapi.fileEditor.TextEditor;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.util.IconLoader;
import com.intellij.openapi.vfs.LocalFileSystem;
import com.intellij.openapi.vfs.VirtualFile;
import com.intellij.ui.JBColor;

import javax.swing.*;
import java.io.File;
import java.util.*;

//此类的主要作用是在代码行中标记错误代码
public class MarkCodeLine {

    //用来存储标记错误信息的map, 存储了所有文件、所有代码行的错误信息, 参数分别代表 文件路径、行数、错误信息, 注意结构为map嵌套map
    private static final Map<String, Map<Integer, MarkCodeMessage>> markMessageMap = new HashMap<>();
    //给错误级别设置权制, 便于比较
    public static final Map<String, Integer> cmp = new HashMap<>();
    static {
        cmp.put("fatal", 4);
        cmp.put("error", 3);
        cmp.put("warning", 2);
        cmp.put("info", 1);
    }

    //往markMessageMap中添加数据, markMessageMap是本类中定义的map
    public static void addFileMarkMessage(ErrorData errorData) {
        if(!markMessageMap.containsKey(errorData.filePath)) {
            //如果当前文件没有存储错误信息的Map<Integer, MarkCodeMessage>实例, 就创建一个添加到markMessageMap中
            List<String> list = new ArrayList<>();
            list.add(errorData.severity + ": " + errorData.msg);

            Map<Integer, MarkCodeMessage> markMessage = new HashMap<>();

            markMessage.put(errorData.line, new MarkCodeMessage(errorData.filePath, errorData.line, errorData.severity, list));
            markMessageMap.put(errorData.filePath, markMessage);
        } else {
            //获取当前文件的Map<Integer, MarkCodeMessage>实例
            Map<Integer, MarkCodeMessage> markMessage = markMessageMap.get(errorData.filePath);
            if (!markMessage.containsKey(errorData.line)) {
                //如果Map<Integer, MarkCodeMessage>实例里没有对应代码行的MarkCodeMessage实例, 就创建一个并放到Map<Integer, MarkCodeMessage>实例里
                List<String> list = new ArrayList<>();
                list.add(errorData.severity + ": " + errorData.msg);
                markMessage.put(errorData.line, new MarkCodeMessage(errorData.filePath, errorData.line, errorData.severity, list));
            } else {
                //如果对应代码行已经有MarkCodeMessage实例存储错误信息就更新MarkCodeMessage实例中的错误信息
                MarkCodeMessage markCodeMessage = markMessage.get(errorData.line);
                markCodeMessage.errorMessage.add(errorData.severity + ": " + errorData.msg);
                if (cmp.get(errorData.severity) > cmp.get(markCodeMessage.severity))
                    markCodeMessage.severity = errorData.severity;
            }
        }
    }


    //标记某个文件里出现错误的代码行
    public static void showMark(String filePath, Project project) {
        //获取对应文件的编辑器
        FileEditorManager fileEditorManager = FileEditorManager.getInstance(project);
        VirtualFile virtualFile = LocalFileSystem.getInstance().findFileByPath(filePath.replace(File.separatorChar, '/'));
        FileEditor[] fileEditors = fileEditorManager.getEditors(virtualFile);
        if(fileEditors.length == 0)
            return;
        Editor editor = null;
        for (FileEditor fileEditor : fileEditors) {
            if (fileEditor instanceof TextEditor) {
                editor = ((TextEditor) fileEditor).getEditor();
            }
        }
        if(editor == null)
            return;
        //获取对应文件的错误信息map
        Map<Integer, MarkCodeMessage> markMessage = markMessageMap.get(filePath);
        if(markMessage == null)
            return;
        //遍历错误信息map, 对每个出现错误的代码行分别处理
        for (Map.Entry<Integer, MarkCodeMessage> entry : markMessage.entrySet()) {
            action(entry.getValue(), editor);
        }
        markMessageMap.remove(filePath);
    }

    //标记某一行代码行
    private static void action(MarkCodeMessage markCodeMessage, Editor editor) {

        MarkupModel markupModel = editor.getMarkupModel();
        //移除之前此代码行里的标记
        markupModel.removeAllHighlighters();

        //设置标记样式
        TextAttributes attributes = new TextAttributes();
        if(cmp.get(markCodeMessage.severity) > 2)
            attributes.setEffectColor(JBColor.RED);
        else
            attributes.setEffectColor(JBColor.yellow);
        attributes.setEffectType(EffectType.LINE_UNDERSCORE);

        int startOffset = editor.getDocument().getLineStartOffset(markCodeMessage.codeLine - 1);
        int endOffset = editor.getDocument().getLineEndOffset(markCodeMessage.codeLine - 1);

        RangeHighlighter highlighter = markupModel.addRangeHighlighter(
                startOffset, endOffset, 0, attributes, HighlighterTargetArea.EXACT_RANGE);

        //设置标记代码行的图标
        highlighter.setGutterIconRenderer(new GutterIconRenderer() {
            //获取图标
            @Override
            public Icon getIcon() {
                if(cmp.get(markCodeMessage.severity) > 2)
                    return IconLoader.getIcon("/icons/error.svg", StartFileAnalysis.class);// 使用错误图标
                else
                    return IconLoader.getIcon("/icons/warning.svg", StartFileAnalysis.class);
            }

            //设置鼠标悬停在图标上时展示的文本
            @Override
            public String getTooltipText() {
                String message = null;
                for(String msg: markCodeMessage.errorMessage)
                    if (message == null)
                        message = msg;
                    else
                        message = message + "<br>" + msg + "</br>";
                return message; // 提供错误信息作为工具提示文本
            }

            @Override
            public boolean equals(Object obj) {
                if (this == obj) return true;
                if (obj == null || getClass() != obj.getClass()) return false;
                return true;
            }

            @Override
            public int hashCode() {
                return Objects.hash(getClass());
            }

            //定义点击图标要执行的操作
            @Override
            public AnAction getClickAction() {
                return null;
            }
        });
    }
}