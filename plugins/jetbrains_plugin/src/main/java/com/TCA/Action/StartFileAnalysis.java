package com.TCA.Action;

import com.TCA.Data.ErrorData;
import com.TCA.Data.FileType;
import com.TCA.Data.ProjectErrorData;
import com.TCA.Setting.AppSettings;
import com.TCA.Window.ProjectAnalysisDataWindow;
import com.TCA.Window.ProjectAnalysisLogsWindow;
import com.TCA.Window.TreeNodeType;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.editor.CaretModel;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.editor.LogicalPosition;
import com.intellij.openapi.editor.ScrollType;
import com.intellij.openapi.fileEditor.FileEditorManager;
import com.intellij.openapi.fileEditor.OpenFileDescriptor;
import com.intellij.openapi.progress.ProgressIndicator;
import com.intellij.openapi.progress.Task;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.vfs.LocalFileSystem;
import com.intellij.openapi.vfs.VirtualFile;
import com.intellij.ui.treeStructure.Tree;
import org.jetbrains.annotations.NotNull;

import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.TreePath;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;
import java.util.Map;
import java.util.Objects;

//此类是普通类, 用于被动作类调用, 实现了文件分析的功能
//具体实现与StartDirectoryAnalysis类似, 可参考StartDirectoryAnalysis中的解释
public class StartFileAnalysis {

    private void createDataTree(AnActionEvent event, File file, String dataPath) {
        ObjectMapper objectMapper = new ObjectMapper();
        String fileName = file.getName();

        FileType rootFile = new FileType(fileName, true);
        DefaultMutableTreeNode root = new DefaultMutableTreeNode(rootFile);
        ProjectErrorData projectErrorData;
        try {
            //从分析结果文件里面读取数据, 根据数据生成ProjectErrorData实例
            projectErrorData = objectMapper.readValue(new File(dataPath), ProjectErrorData.class);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        DefaultMutableTreeNode node;
        //文件分析中结果树的层数有限, 最多是三层, 不需要使用DFS构建
        //遍历分析出的所有错误数据
        for(Map.Entry<String, List<ErrorData>> entry: projectErrorData.issue_detail.entrySet()) {
            for (ErrorData errorData : entry.getValue()) {
                if(entry.getKey().equals(fileName)) {

                    errorData.filePath = file.getPath();
                    rootFile.countIssue(errorData.severity);

                    node = new DefaultMutableTreeNode(errorData);
                    root.add(node);
                    MarkCodeLine.addFileMarkMessage(errorData);
                }
            }
            MarkCodeLine.showMark(file.getPath(), event.getProject());
        }
        TreeNodeType.deleteBlankNode(root);
        Tree tree = new Tree(root);
        tree.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                if (e.getClickCount() == 2) { // 检测双击事件
                    // 获取双击位置的树路径
                    TreePath path = tree.getPathForLocation(e.getX(), e.getY());
                    if (path != null) {
                        // 获取双击的节点node
                        DefaultMutableTreeNode node = (DefaultMutableTreeNode) path.getLastPathComponent();
                        ErrorData errorData = (ErrorData) node.getUserObject();
                        if(errorData.line == -1)
                            return;
                        jumpToLine(errorData, event, file.getPath());
                    }
                }
            }
        });

        tree.setCellRenderer(new TreeNodeType());

        ProjectAnalysisDataWindow.setDataTree(tree, event.getProject().getBasePath());
    }

    private void jumpToLine(ErrorData errorData, AnActionEvent event, String filePath) {
        Project project = event.getProject();
        FileEditorManager fileEditorManager = FileEditorManager.getInstance(project);
        VirtualFile virtualFile = LocalFileSystem.getInstance().findFileByPath(filePath.replace(File.separatorChar, '/'));
        Editor editor = fileEditorManager.openTextEditor(new OpenFileDescriptor(project, virtualFile), true);

        if (editor != null) {
            CaretModel caretModel = editor.getCaretModel();
            LogicalPosition pos = new LogicalPosition(errorData.line - 1, errorData.column - 1);
            caretModel.moveToLogicalPosition(pos);
            editor.getScrollingModel().scrollToCaret(ScrollType.CENTER);
        }
    }

//    @Override
    public void actionPerformed(AnActionEvent event) {

        AppSettings.State state = Objects.requireNonNull(AppSettings.getInstance().getState());
        Project project = event.getProject();

        File file = new File(state.sourceDir);

        File workDir = new File(state.codeAnalysisClientPath);
        String initCommand = "";
        initCommand = initCommand + state.ePythonPath;
        initCommand = initCommand + " codepuppy.py";
        initCommand = initCommand + " quickinit";
        initCommand = initCommand + " -t " + state.token;
        initCommand = initCommand + " --scheme-template-id " + state.schemeTemplateId;
        initCommand = initCommand + " --org-sid " + state.orgSid;

        String runCommand = "";
        runCommand = runCommand + state.ePythonPath;
        runCommand = runCommand + " codepuppy.py";
        runCommand = runCommand + " quickscan";
        runCommand = runCommand + " -t " + state.token;
        runCommand = runCommand + " --scheme-template-id " + state.schemeTemplateId;
        runCommand = runCommand + " --org-sid " + state.orgSid;
        runCommand = runCommand + " -s " + file.getPath().substring(0, file.getPath().length() - file.getName().length());
        runCommand = runCommand + " --file " + file.getName();

        String finalRunCommand = runCommand;
        String finalInitCommand = initCommand;
        new Task.Backgroundable(project, "执行代码分析", false) {
            @Override
            public void run(@NotNull ProgressIndicator indicator) {

                System.out.println(finalInitCommand);
                System.out.println(finalRunCommand);
                ProcessBuilder processBuilder = new ProcessBuilder();
                //获取操作系统环境变量并变为小些
                String OS = System.getProperty("os.name").toLowerCase();
                if(OS.contains("win"))
                    processBuilder.command("cmd", "/c", finalInitCommand + "&&" + finalRunCommand);
                else
                    processBuilder.command("bash", "-c", finalInitCommand + "&&" + finalRunCommand);
                processBuilder.directory(workDir);
                Map<String, String> environment = processBuilder.environment();
                environment.put("PATH", state.pythonPath + ":" + environment.get("PATH"));

                Process process;
                try {
                    process = processBuilder.start();
                    new Thread(() -> {
                        try {
                            String line;
                            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                            while ((line = reader.readLine()) != null) {
                                ProjectAnalysisLogsWindow.addText(line, project.getBasePath());
                            }
                        } catch (IOException e) {
                            throw new RuntimeException(e);
                        }
                    }).start();

                    new Thread(() ->{
                        try {
                            String line;
                            BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                            while ((line = errorReader.readLine()) != null) {
                                ProjectAnalysisLogsWindow.addText(line, project.getBasePath());
                            }
                        } catch (IOException e) {
                            throw new RuntimeException(e);
                        }
                    }).start();
                    process.waitFor();
                    createDataTree(event, file, state.codeAnalysisClientPath + "/tca_quick_scan_report.json");
                } catch (Exception e) {
                    ProjectAnalysisLogsWindow.addText(e.toString(), project.getBasePath());
                    throw new RuntimeException(e);
                }
            }
        }.queue();
    }
}