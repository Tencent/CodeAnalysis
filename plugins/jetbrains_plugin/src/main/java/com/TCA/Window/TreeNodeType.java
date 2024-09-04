package com.TCA.Window;

import com.TCA.Action.MarkCodeLine;
import com.TCA.Action.StartFileAnalysis;
import com.TCA.Data.ErrorData;
import com.TCA.Data.FileType;
import com.intellij.openapi.util.IconLoader;

import javax.swing.*;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.TreeCellRenderer;
import java.awt.*;

//此类主要用于设置结果树中节点的展示样式, 具体方法为用label实例替代原来的节点, 以此达到修改样式的目的, 还用于删除结果树中错误数为0的目录和文件
public class TreeNodeType implements TreeCellRenderer {

    private JLabel label;

    public TreeNodeType() {
        label = new JLabel();
        label.setOpaque(true);
    }

    @Override
    public Component getTreeCellRendererComponent(JTree tree, Object value, boolean selected, boolean expanded, boolean leaf, int row, boolean hasFocus) {
        //获取当前节点
        DefaultMutableTreeNode node = (DefaultMutableTreeNode) value;
        Object userObject = node.getUserObject();

        //使用label代替原来的节点, 设置label的文本
        label.setText(userObject.toString());

        //设置label的图标
        //判断当前节点是否是目录或文件节点
        if(userObject instanceof FileType fileType) {
            //是文件或目录节点
            //根据节点是目录还是文件设置对应的图标
            if(fileType.isDirectory) {
                label.setIcon(IconLoader.getIcon("/icons/directory.svg", StartFileAnalysis.class));
            } else {
                label.setIcon(IconLoader.getIcon("/icons/file.svg", StartFileAnalysis.class));
            }
        }
        else {
            //当前节点是错误信息节点
            ErrorData errorData = (ErrorData) userObject;
            //根据错误等级设置图标
            if(MarkCodeLine.cmp.get(errorData.severity) > 2)
                label.setIcon(IconLoader.getIcon("/icons/error.svg", StartFileAnalysis.class));
            else
                label.setIcon(IconLoader.getIcon("/icons/warning.svg", StartFileAnalysis.class));
        }
        return label;
    }

    //DFS删除结果树中错误数为 0 的目录和文件
    public static void deleteBlankNode (DefaultMutableTreeNode node) {
        //for循环遍历node的所有孩子节点
        for(int i = 0; i < node.getChildCount(); i++) {
            DefaultMutableTreeNode childNode = (DefaultMutableTreeNode) node.getChildAt(i);
            Object object = childNode.getUserObject();
            if (object instanceof FileType fileType) {
                //孩子节点是目录或文件节点, 就判断错误数量是否为0, 为0就删除该节点
                if (fileType.sum == 0) {
                    node.remove(i);
                    i--;
                }
                else {
                    //否则递归继续寻找错误数量为0的节点
                    deleteBlankNode(childNode);
                }
            } else {
                return;
            }
        }
    }
}
