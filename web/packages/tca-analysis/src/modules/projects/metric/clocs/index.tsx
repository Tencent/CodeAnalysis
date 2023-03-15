// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 度量结果 - 代码统计
 */
import React, { useEffect, useState } from 'react';
import { Tree, Row, Col, Descriptions, Tooltip, Tag, Button } from 'coding-oa-uikit';
import { t } from '@src/utils/i18n';
import QuestionCircleIcon from 'coding-oa-uikit/lib/icon/QuestionCircle';
import ArrowLeftIcon from 'coding-oa-uikit/lib/icon/ArrowLeft';
import { forEach, get } from 'lodash';

// 项目内
import NoDataSVG from '@src/images/no-data.svg';
import { getClocFiles } from '@src/services/projects';
import s from '../style.scss';

const { DirectoryTree } = Tree;

const CHANGE_TYPE = {
  ADD: 'add',
  MOD: 'mod',
  DEL: 'del',
};

interface DataNode {
  title: string;
  key: string;
  isLeaf?: boolean;
  children?: DataNode[];
}


interface IProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  projectId: number;
}

const Clocs = ({ orgSid, teamName, repoId, projectId }: IProps) => {
  const [treeData, setTreeData] = useState<Array<any>>([]);
  const [rootNodeInfo, setRootNodeInfo] = useState<any>({});
  const [selectNodeInfo, setSelectNodeInfo] = useState<any>({});

  useEffect(() => {
    // 初始化获取根节点数据
    getClocFiles(orgSid, teamName, repoId, projectId).then((response) => {
      setTreeData(formatData(response));
      const { info = {} } = response;
      const tempRootNodeInfo = {};
      forEach(info, (value, key) => {
        const newKey = key.replace('__sum', '');
        tempRootNodeInfo[newKey] = value;
      });
      setRootNodeInfo(tempRootNodeInfo);
      setSelectNodeInfo(tempRootNodeInfo);
    });
  }, [projectId]);

  /**
 * 将请求数据格式化为tree所需数据
 * @param data getClocFiles返回数据
 */
  const formatData = (data: any) => {
    const nodes: Array<any> = [];
    forEach(data, (value, key) => {
      switch (key) {
        case 'dirs':
          forEach(value.results, (info) => {
            const dict: any = {
              info,
            };
            if (info.dir_path) {
              if (info.parent_path) {
              // 父目录不为根目录
              // eslint-disable-next-line
              dict.title = info.dir_path.split(`${info.parent_path}/`)[1];
              } else {
              // 父目录为根目录
                dict.title = info.dir_path;
              }
              dict.key = info.dir_path;
              nodes.push(dict);
            }
          });
          break;
        case 'files':
          forEach(value.results, (info) => {
            let title = info.file_name;
            switch (info.change_type) {
              case CHANGE_TYPE.ADD:
                title = (
                <>
                  <Tag className={s.clocTagBlue} color="blue">{t('新增')}</Tag> {title}
                </>
                );
                break;
              case CHANGE_TYPE.MOD:
                title = (
                <>
                  <Tag className={s.clocTagGreen} color="green">{t('修改')}</Tag> {title}
                </>
                );
                break;
              case CHANGE_TYPE.DEL:
                title = (
                <>
                  <Tag className={s.clocTagRed} color="red">{t('修改')}</Tag> {title}
                </>
                );
                break;
              default:
                break;
            }
            nodes.push({
              info,
              title,
              isLeaf: true,
              key: info.dir_path ? `${info.dir_path}/${info.file_name}` : info.file_name,
            });
          });
          break;
        default:
          break;
      }
    });
    return nodes;
  };

  /**
     * 切换时，选中节点信息
     * @param keys
     * @param event
     */
  const onSelect = (keys: Array<string | number>, event: any) => {
    const info = get(event, 'node.info', {});
    info.label = get(event, 'node.title', null);
    setSelectNodeInfo(info);
  };

  /**
     * 遍历更新树结构
     * @param list
     * @param key
     * @param children
     */
  const updateTreeData = (list: DataNode[], key: React.Key, children: DataNode[]): DataNode[] => list.map((node) => {
    if (node.key === key) {
      return {
        ...node,
        children,
      };
    }
    if (node.children) {
      return {
        ...node,
        children: updateTreeData(node.children, key, children),
      };
    }
    return node;
  });

  /**
     * 异步加载数据
     * @param node 节点
     */
  const onLoadData = (node: any): Promise<void> => new Promise((resolve) => {
    const path = node.info.dir_path;
    const { key } = node;
    getClocFiles(orgSid, teamName, repoId, projectId, path)
      .then((response) => {
        const nodes = formatData(response);
        setTreeData(origin => updateTreeData(origin, key, nodes));
      })
      .finally(() => {
        resolve();
      });
  });

  if (treeData.length === 0) {
    return (
      <div className=" text-center" style={{ margin: '150px' }}>
        <img src={NoDataSVG} alt="no-data" />
        <p className=" text-grey-6 fs-12 mt-sm">
          {t('暂无代码统计信息，请确认是否开启该功能')}
        </p>
      </div>
    );
  }

  return (
    <Row gutter={20}>
      <Col flex="320px">
        <div className={s.clocsLeftContainer}>
          <DirectoryTree
            loadData={onLoadData}
            multiple
            onSelect={onSelect}
            treeData={treeData}
          />
        </div>
      </Col>
      <Col flex="auto">
        <div className={s.clocsRightContainer}>
          <div className={s.header}>
            <p className={s.tit}>
              {selectNodeInfo.label ? (
                <>
                  <Tooltip title={t('回到根目录详情')}>
                    <Button
                      className={s.backIcon}
                      icon={<ArrowLeftIcon />}
                      type="text"
                      shape="circle"
                      onClick={() => setSelectNodeInfo(rootNodeInfo)}
                    />
                  </Tooltip>

                  <span className="inline-block vertical-middle">
                    {selectNodeInfo.label}
                  </span>
                </>
              ) : (
                t('根目录')
              )}
            </p>
            <p className={s.desc}>
              {selectNodeInfo.file_num && (
                <span className="mr-20">
                  {t('子文件：')}
                  {selectNodeInfo.file_num}
                </span>
              )}
              <span className="mr-20">
                {t('代码行：')}
                {selectNodeInfo.code_line_num}
              </span>
              <span className="mr-20">
                {t('注释行：')}
                {selectNodeInfo.comment_line_num}
              </span>
              <span className="mr-20">
                {t('空白行：')}
                {selectNodeInfo.blank_line_num}
              </span>
              <span className="mr-20">
                {t('总行数：')}
                {selectNodeInfo.total_line_num}
              </span>
            </p>
          </div>
          <div className={s.body}>
            <p className={s.tit}>
              {t('差异化')}{' '}
              <Tooltip
                placement="right"
                title={t('最近一次分析相对上次分析结果的比较。当前数据仅包含一级子文件的统计结果，不包含孙子文件的结果')}
              >
                <QuestionCircleIcon className="ml-xs" />
              </Tooltip>
            </p>
            <Descriptions bordered layout="vertical" size="small">
              <Descriptions.Item label={t('新增')}>
                <div>
                  {t('代码行：')}
                  {selectNodeInfo.add_code_line_num}
                </div>
                <div>
                  {t('注释行：')}
                  {selectNodeInfo.add_comment_line_num}
                </div>
                <div>
                  {t('空白行：')}
                  {selectNodeInfo.add_blank_line_num}
                </div>
                <div>
                  {t('总行数：')}
                  {selectNodeInfo.add_total_line_num}
                </div>
              </Descriptions.Item>
              <Descriptions.Item label={t('修改')}>
                <div>
                  {t('代码行：')}
                  {selectNodeInfo.mod_code_line_num}
                </div>
                <div>
                  {t('注释行：')}
                  {selectNodeInfo.mod_comment_line_num}
                </div>
                <div>
                  {t('空白行：')}
                  {selectNodeInfo.mod_blank_line_num}
                </div>
                <div>
                  {t('总行数：')}
                  {selectNodeInfo.mod_total_line_num}
                </div>
              </Descriptions.Item>
              <Descriptions.Item label={t('删除')}>
                <div>
                  {t('代码行：')}
                  {selectNodeInfo.del_code_line_num}
                </div>
                <div>
                  {t('注释行：')}
                  {selectNodeInfo.del_comment_line_num}
                </div>
                <div>
                  {t('空白行：')}
                  {selectNodeInfo.del_blank_line_num}
                </div>
                <div>
                  {t('总行数：')}
                  {selectNodeInfo.del_total_line_num}
                </div>
              </Descriptions.Item>
            </Descriptions>
          </div>
        </div>
      </Col>
    </Row>
  );
};
export default Clocs;
