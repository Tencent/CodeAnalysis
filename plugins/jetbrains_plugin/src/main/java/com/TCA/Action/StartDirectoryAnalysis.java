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

//此类是普通类, 用于被动作类调用, 实现了目录分析的功能
public class StartDirectoryAnalysis {

    //DFS建立结果树
    void addFileNode(DefaultMutableTreeNode root, File file, Map<String, List<ErrorData>> map, String bashPath, FileType fileType, AnActionEvent event) {
        if(file.isDirectory()) {
            //如果当前文件是目录
            for (File f: file.listFiles()) {
                //遍历目录下所有文件
                DefaultMutableTreeNode node;
                FileType childFileType;
                //根据f是否是目录创建不同的FileType实例, 以便后面能够区分树上节点是否是目录
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
                //把孩子节点的错误数量加到父亲节点上
                fileType.fatal = fileType.fatal + childFileType.fatal;
                fileType.error = fileType.error + childFileType.error;
                fileType.warning = fileType.warning + childFileType.warning;
                fileType.info = fileType.info + childFileType.info;
                fileType.sum = fileType.sum + childFileType.sum;
            }
        } else {
            //如果当前文件不是目录
            if(file.getPath().length() >= bashPath.length()) {
                //获取当前文件错误数据
                List<ErrorData> list = map.get(file.getPath().substring(bashPath.length()));
                if(list == null)
                    return;
                for (ErrorData errorData: list) {
                    //遍历文件的所有错误数据
                    errorData.filePath = file.getPath();
                    //把错误数据添加到存储标记代码行数据的map中
                    MarkCodeLine.addFileMarkMessage(errorData);
                    DefaultMutableTreeNode node = new DefaultMutableTreeNode(errorData);
                    root.add(node);
                    //根据错误种类修改文件的错误数
                    fileType.countIssue(errorData.severity);
                }
                //把该文件的错误数据从map中移除
                map.remove(file.getPath().substring(bashPath.length()));
                //标记该文件中出现错误的代码行
                MarkCodeLine.showMark(file.getPath(), event.getProject());
            }
        }
    }

    //创建结果树
    private void createDataTree(AnActionEvent event, String dataPath, String basePath) {
        ObjectMapper objectMapper = new ObjectMapper();
        File file = new File(basePath);

        ProjectErrorData projectErrorData;
        try {
            //从分析结果文件里面读取数据, 根据数据生成ProjectErrorData实例
            projectErrorData = objectMapper.readValue(new File(dataPath), ProjectErrorData.class);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        //获取问题详情列表
        Map<String, List<ErrorData>> map = projectErrorData.issue_detail;

        //创建结果树的根节点
        FileType rootFileType = new FileType(file.getName(), true);
        FileType otherFileType = new FileType("OtherError", true);
        //创建结果树的根节点, DefaultMutableTreeNode是树的节点, FileType是树节点的数据
        DefaultMutableTreeNode root = new DefaultMutableTreeNode(rootFileType);
        DefaultMutableTreeNode other = new DefaultMutableTreeNode(otherFileType);
        //执行DFS建树, 统计目录和文件错误数量, 标记错误代码行
        addFileNode(root, file, map, basePath, rootFileType, event);

        //建完树之后剩下的错误数据不属于单个文件, 而是属于整个项目, 把他们添加到OtherError节点下
        for(Map.Entry<String, List<ErrorData>> entry: map.entrySet()) {
            for (ErrorData errorData: entry.getValue()) {
                //把不属于单个文件的错误行数设为-1
                errorData.line = -1;
                otherFileType.countIssue(errorData.severity);
                DefaultMutableTreeNode node = new DefaultMutableTreeNode(errorData);
                other.add(node);
            }
        }
        root.add(other);
        //调用函数删除结果树中没有出现错误的目录或文件
        TreeNodeType.deleteBlankNode(root);
        //使用DefaultMutableTreeNode类创建Tree实例
        Tree tree = new Tree(root);
        //配置双击跳转功能
        tree.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                if (e.getClickCount() == 2) { // 检测双击事件
                    // 获取双击位置的树路径
                    TreePath path = tree.getPathForLocation(e.getX(), e.getY());
                    if (path != null) {
                        // 获取双击的节点
                        DefaultMutableTreeNode node = (DefaultMutableTreeNode) path.getLastPathComponent();
                        ErrorData errorData = (ErrorData) node.getUserObject();
                        //等于-1代表错误不属于某个文件
                        if(errorData.line == -1)
                            return;
                        jumpToLine(errorData, event, errorData.filePath);
                    }
                }
            }
        });
        //设置结果树的展示样式
        tree.setCellRenderer(new TreeNodeType());
        //更新结果窗口中的结果树
        ProjectAnalysisDataWindow.setDataTree(tree, event.getProject().getBasePath());
    }

    private void jumpToLine(ErrorData errorData, AnActionEvent event, String filePath) {
        //跳转到出现错误的行
        //获取要跳转的文件的editor
        Project project = event.getProject();
        FileEditorManager fileEditorManager = FileEditorManager.getInstance(project);
        VirtualFile virtualFile = LocalFileSystem.getInstance().findFileByPath(filePath.replace(File.separatorChar, '/'));
        Editor editor = fileEditorManager.openTextEditor(new OpenFileDescriptor(project, virtualFile), true);

        //使用editor设置光标的位置
        if (editor != null) {
            CaretModel caretModel = editor.getCaretModel();
            LogicalPosition pos = new LogicalPosition(errorData.line - 1, errorData.column - 1);
            caretModel.moveToLogicalPosition(pos);
            editor.getScrollingModel().scrollToCaret(ScrollType.CENTER);
        }
    }

    public void actionPerformed(@NotNull AnActionEvent event) {
        //获取执行此函数的project环境和参数设置服务的实例
        Project project = event.getProject();
        AppSettings.State state = Objects.requireNonNull(AppSettings.getInstance().getState());

        //脚本的工作目录
        File workDir = new File(state.codeAnalysisClientPath);
        //初始化工具命令
        String initCommand = "";
        initCommand = initCommand + state.ePythonPath;
        initCommand = initCommand + " codepuppy.py";
        initCommand = initCommand + " quickinit";
        initCommand = initCommand + " -t " + state.token;
        initCommand = initCommand + " --scheme-template-id " + state.schemeTemplateId;
        initCommand = initCommand + " --org-sid " + state.orgSid;

        //快速分析命令
        String runCommand = "";
        runCommand = runCommand + state.ePythonPath;
        runCommand = runCommand + " codepuppy.py";
        runCommand = runCommand + " quickscan";
        runCommand = runCommand + " -t " + state.token;
        runCommand = runCommand + " --scheme-template-id " + state.schemeTemplateId;
        runCommand = runCommand + " --org-sid " + state.orgSid;
        runCommand = runCommand + " -s " + state.sourceDir;

        String finalRunCommand = runCommand;
        String finalInitCommand = initCommand;
        //创建线程执行命令
        new Task.Backgroundable(project, "执行目录下全文件分析", false) {
            @Override
            public void run(@NotNull ProgressIndicator indicator) {
                //使用ProcessBuilder运行脚本
                ProcessBuilder processBuilder = new ProcessBuilder();
                //设置要执行的脚本
                String OS = System.getProperty("os.name").toLowerCase();
                //获取操作系统环境变量并变为小些
                if(OS.contains("win"))
                    processBuilder.command("cmd", "/c", finalInitCommand + "&&" + finalRunCommand);
                else
                    processBuilder.command("bash", "-c", finalInitCommand + "&&" + finalRunCommand);
                //设置工作目录
                processBuilder.directory(workDir);
                //更新ProcessBuilder新建进程的环境变量
                Map<String, String> environment = processBuilder.environment();
                environment.put("PATH", state.pythonPath + ":" + environment.get("PATH"));

                Process process;
                try {
                    //执行线程
                    process = processBuilder.start();
                    //创建两个新的线程读取线程的输出
                    new Thread(() -> {
                        try {
                            String line;
                            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                            while ((line = reader.readLine()) != null) {
                                //把输出打印到分析日志标签页
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
                                //把输出打印到分析日志标签页
                                ProjectAnalysisLogsWindow.addText(line, project.getBasePath());
                            }
                        } catch (IOException e) {
                            throw new RuntimeException(e);
                        }
                    }).start();
                    //等待process线程执行结束
                    process.waitFor();
                    //创建结果树
                    createDataTree(event, state.codeAnalysisClientPath + "/tca_quick_scan_report.json", state.sourceDir + "/");
                } catch (Exception e) {
                    //打印错误信息到日志窗口
                    ProjectAnalysisLogsWindow.addText(e.toString(), project.getBasePath());
                    throw new RuntimeException(e);
                }
            }
        }.queue();
    }
}
