package com.TCA.Action;

import com.TCA.Data.ErrorData;
import com.TCA.Data.FileType;
import com.TCA.Data.ProjectErrorData;
import com.TCA.Setting.AppSettings;
import com.TCA.Window.ProjectAnalysisDataWindow;
import com.TCA.Window.ProjectAnalysisLogsWindow;
import com.TCA.Window.TreeNodeType;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.actionSystem.Presentation;
import com.intellij.openapi.editor.CaretModel;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.editor.LogicalPosition;
import com.intellij.openapi.editor.ScrollType;
import com.intellij.openapi.fileEditor.FileEditorManager;
import com.intellij.openapi.fileEditor.OpenFileDescriptor;
import com.intellij.openapi.progress.ProgressIndicator;
import com.intellij.openapi.progress.Task;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.util.IconLoader;
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

//此类是动作类, 实现了工程分析的功能
//具体实现与StartDirectoryAnalysis类似, 可参考StartDirectoryAnalysis中的解释, 不同的是此类在配置文件中进行了注册, 用户可以直接使用此类, 而不是通过动作类调用此类
public class StartProjectAnalysis extends AnAction{
    private static Boolean isEnable = true;

    public StartProjectAnalysis() {
        // 设置动作的名称和图标，在工具栏或菜单中显示
        super("开启工程分析", "", IconLoader.getIcon("/icons/runProject.svg", MenuSelect.class));
    }

    @Override
    public void update(@NotNull AnActionEvent event) {
        Presentation presentation = event.getPresentation();
        presentation.setEnabled(isEnable);
    }

    private void unUseButton(AnActionEvent event) {
        isEnable = false;
        update(event);
        Presentation presentation = event.getPresentation();
        presentation.setIcon(IconLoader.getIcon("/icons/canNotRun.svg", StartFileAnalysis.class));
    }

    private void useButton(AnActionEvent event) {
        isEnable = true;
        update(event);
        Presentation presentation = event.getPresentation();
        presentation.setIcon(IconLoader.getIcon("/icons/runProject.svg", StartFileAnalysis.class));
    }

    void addFileNode(DefaultMutableTreeNode root, File file, Map<String, List<ErrorData>> map, String bashPath, FileType fileType, AnActionEvent event) {
        if(file.isDirectory()) {
            for (File f: file.listFiles()) {
                DefaultMutableTreeNode node;
                FileType childFileType;
                if (f.isDirectory()) {
                    childFileType = new FileType(f.getName(), true);
                    node = new DefaultMutableTreeNode(childFileType);
                }
                else {
                    childFileType = new FileType(f.getName(), false);
                    node = new DefaultMutableTreeNode(childFileType);
                }
                root.add(node);
                addFileNode(node, f, map, bashPath, childFileType, event);
                fileType.fatal = fileType.fatal + childFileType.fatal;
                fileType.error = fileType.error + childFileType.error;
                fileType.warning = fileType.warning + childFileType.warning;
                fileType.info = fileType.info + childFileType.info;
                fileType.sum = fileType.sum + childFileType.sum;
            }
        } else {
            if(file.getPath().length() >= bashPath.length()) {
                List<ErrorData> list = map.get(file.getPath().substring(bashPath.length()));
                if(list == null)
                    return;
                for (ErrorData errorData: list) {

                    errorData.filePath = file.getPath();
                    MarkCodeLine.addFileMarkMessage(errorData);
                    DefaultMutableTreeNode node = new DefaultMutableTreeNode(errorData);
                    root.add(node);
                    fileType.countIssue(errorData.severity);
                }
                map.remove(file.getPath().substring(bashPath.length()));
                MarkCodeLine.showMark(file.getPath(), event.getProject());
            }
        }
    }

    private void createDataTree(AnActionEvent event, String dataPath) {
        ObjectMapper objectMapper = new ObjectMapper();
        Project project = event.getProject();

        ProjectErrorData projectErrorData;
        try {
            projectErrorData = objectMapper.readValue(new File(dataPath), ProjectErrorData.class);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        Map<String, List<ErrorData>> map = projectErrorData.issue_detail;

        FileType rootFileType = new FileType(project.getName(), true);
        FileType otherFileType = new FileType("OtherError", true);
        File file = new File(project.getBasePath());

        DefaultMutableTreeNode root = new DefaultMutableTreeNode(rootFileType);
        DefaultMutableTreeNode other = new DefaultMutableTreeNode(otherFileType);
        addFileNode(root, file, map, project.getBasePath() + "/", rootFileType, event);

        for(Map.Entry<String, List<ErrorData>> entry: map.entrySet()) {
            for (ErrorData errorData: entry.getValue()) {
                errorData.line = -1;
                otherFileType.countIssue(errorData.severity);
                DefaultMutableTreeNode node = new DefaultMutableTreeNode(errorData);
                other.add(node);
            }
        }
        root.add(other);
        TreeNodeType.deleteBlankNode(root);
        Tree tree = new Tree(root);
        tree.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                if (e.getClickCount() == 2) { // 检测双击事件
                    // 获取双击位置的树路径
                    TreePath path = tree.getPathForLocation(e.getX(), e.getY());

                    if (path != null) {
                        // 获取双击的节点
                        DefaultMutableTreeNode node = (DefaultMutableTreeNode) path.getLastPathComponent();
                        if(node.getUserObject() instanceof ErrorData errorData) {
                            if(errorData.line == -1)
                                return;
                            jumpToLine(errorData, event, errorData.filePath);
                        }
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

    public void actionPerformed(@NotNull AnActionEvent event) {
        unUseButton(event);

        Project project = event.getProject();

        AppSettings.State state = Objects.requireNonNull(AppSettings.getInstance().getState());

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
        runCommand = runCommand + " -s " + project.getBasePath();

        String finalRunCommand = runCommand;
        String finalInitCommand = initCommand;
        new Task.Backgroundable(project, "执行工程分析", false) {
            @Override
            public void run(@NotNull ProgressIndicator indicator) {
                System.out.println(finalInitCommand);
                System.out.println(finalRunCommand);
                ProcessBuilder processBuilder = new ProcessBuilder();
                String OS = System.getProperty("os.name").toLowerCase();
                //获取操作系统环境变量并变为小些
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
                    createDataTree(event, state.codeAnalysisClientPath + "/tca_quick_scan_report.json");
                    useButton(event);
                } catch (Exception e) {
                    ProjectAnalysisLogsWindow.addText(e.toString(), project.getBasePath());
                    throw new RuntimeException(e);
                } finally {
                    useButton(event);
                }
            }
        }.queue();
    }
}
