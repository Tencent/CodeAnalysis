package com.TCA.Listener;

import com.TCA.Action.MarkCodeLine;
import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.fileEditor.FileEditorManager;
import com.intellij.openapi.fileEditor.FileEditorManagerListener;
import com.intellij.openapi.vfs.VirtualFile;
import org.jetbrains.annotations.NotNull;

//用于监听文件打开操作的类
public class FileListener implements FileEditorManagerListener {

    @Override
    public void fileOpened(@NotNull FileEditorManager source, @NotNull VirtualFile file) {
        //当文件打开时执行此函数, 标记打开文件里出现错误的代码行
        MarkCodeLine.showMark(file.getPath(),  source.getProject());
    }
}
