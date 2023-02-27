// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState, useEffect } from 'react';
import cn from 'classnames';
import { isEmpty, pick, isArray } from 'lodash';
import { saveAs } from 'file-saver';

import { Dropdown, Menu, Tooltip, Modal, message, Upload, Button } from 'coding-oa-uikit';
import EllipsisH from 'coding-oa-uikit/lib/icon/EllipsisH';

import {
  getScanDir,
  addScanDir,
  delAllScanDir,
  importScanDir,
  getSysPath,
} from '@src/services/schemes';
import { SCAN_TYPES, PATH_TYPES } from '../constants';

import List from './cus-list';
import SysList from './sys-list';
import AddModal from './modal';

import style from './style.scss';

const initialPager = {
  count: 0,
  pageStart: 0,
  pageSize: 10,
};

interface PathProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  schemeId: number;
}

const Path = (props: PathProps) => {
  const { orgSid, teamName, repoId, schemeId } = props;
  const [tab, setTab] = useState('cus');
  const [cusList, setCusList] = useState([]);
  const [pager, setPager] = useState(initialPager);
  const { pageSize, pageStart } = pager;

  const [visible, setVisible] = useState(false);
  const [importModalVsb, setImportModalVsb] = useState(false);
  const [importModalData, setImportModalData] = useState([]);

  const [sysList, setSysList] = useState([]);

  useEffect(() => {
    getListData(initialPager.pageStart, initialPager.pageSize);

    schemeId && getSysList();
  }, [schemeId]);

  /**
   * 获取自定义过滤路径
   * @param offset
   * @param limit
   */
  const getListData = (offset: number = pageStart, limit: number = pageSize) => {
    if (schemeId) {
      getScanDir(orgSid, teamName, repoId, schemeId, { offset, limit }).then((response) => {
        setPager({
          pageSize: limit,
          pageStart: offset,
          count: response.count,
        });
        setCusList(response.results || []);
      });
    }
  };

  /**
   * 获取系统过滤路径
   */
  const getSysList = () => {
    getSysPath(orgSid, teamName, repoId, schemeId, {
      exclude: 1,
    }).then((response: any) => {
      const res = response.results || [];
      getSysPath(orgSid, teamName, repoId, schemeId).then((response: any) => {
        setSysList(res.concat((response?.results ?? []).map((item: any) => ({
          ...item,
          switch: true,
        }))));
      });
    });
  };

  /**
   * 导出路径配置
   */
  const exportScanDir = () => {
    getScanDir(orgSid, teamName, repoId, schemeId, { limit: pager.count }).then((response: any) => {
      const res = response?.results?.map((item: object) => pick(item, ['dir_path', 'path_type', 'scan_type'])) ?? [];
      const blob = new Blob([JSON.stringify(res)], { type: 'text/plain;charset=utf-8' });
      saveAs(blob, 'path_confs.json');
      message.success('导出成功');
    });
  };

  /**
   * 批量导入路径配置
   */
  const importScanDirHandle = (dirs: object) => {
    importScanDir(orgSid, teamName, repoId, schemeId, dirs).then((response: any) => {
      message.success(`${response.detail || '导入成功'}`);
      getListData(initialPager.pageStart, pageSize);
      setImportModalVsb(false);
    });
  };

  /**
   * 手动上传处理
   * @param file
   */
  const handleUpload = (file: any) => {
    if (file) {
      const reader = new FileReader();
      reader.readAsText(file, 'UTF-8');
      reader.onload = function () {
        setImportModalVsb(true);
        if (this.result) {
          setImportModalData(JSON.parse(this.result as string));
        }
      };
    }
    return false;
  };

  /**
   * 添加过滤路径
   * @param data
   */
  const onAdd = (data: any) => {
    addScanDir(orgSid, teamName, repoId, schemeId, data).then(() => {
      getListData(pageStart, pageSize);
      message.success('添加成功');
      setVisible(false);
    });
  };

  /**
   * 清空过滤路径
   */
  const onDelAll = () => {
    Modal.confirm({
      title: '清空自定义过滤路径',
      content: '确定清空该分析方案的所有过滤路径配置？',
      onOk: () => {
        delAllScanDir(orgSid, teamName, repoId, schemeId).then(() => {
          message.success('清空成功');
          getListData(initialPager.pageStart, pageSize);
        });
      },
    });
  };

  return (
    <div className={style.path}>
      <div className={style.header}>
        <div className={style.tab}>
          <span
            className={cn(style.tabItem, { [style.active]: tab === 'cus' })}
            onClick={() => setTab('cus')}
          >
            自定义
          </span>
          <span
            className={cn(style.tabItem, { [style.active]: tab === 'sys' })}
            onClick={() => setTab('sys')}
          >
            系统默认
          </span>
        </div>
        {tab === 'cus' && (
          <div className={style.operation}>
            <Button onClick={() => setVisible(true)}>添加过滤路径</Button>
            <Dropdown
              placement='bottomRight'
              overlay={
                <Menu className={style.menu} onClick={({ domEvent }) => domEvent.stopPropagation()}>
                  <Menu.Item key='import'>
                    <Upload
                      beforeUpload={handleUpload}
                      fileList={[]}
                    >
                      <Tooltip
                        placement="left"
                        overlayClassName={style.importTooltip}
                        getPopupContainer={() => document.body}
                        title={
                          <span>
                            配置提示：<br />
                      参数：dir_path表示路径；<br />
                      path_type表示路径类型，1为通配符，2为正则表达式；<br />
                      scan_type表示过滤类型，1为只分析，2为只屏蔽；<br />
                      [{'{"dir_path": "xxx", "path_type": 1, "scan_type": 1}'},…]
                    </span>
                        }>
                        <span>导入路径配置</span>
                      </Tooltip>
                    </Upload>
                  </Menu.Item>
                  {
                    !isEmpty(cusList) && ([
                      <Menu.Item key='export' onClick={exportScanDir}>导出路径配置</Menu.Item>,
                      <Menu.Item
                        key='delAll'
                        onClick={onDelAll}
                        className={style.delAll}
                      >一键清空路径配置</Menu.Item>,
                    ])
                  }
                </Menu>
              }>
              <Button className={style.more} onClick={(e: any) => e.stopPropagation()}>
                <EllipsisH />
              </Button>
            </Dropdown>
            <Modal
              visible={importModalVsb}
              title='批量添加过滤路径'
              className={style.importModal}
              onCancel={() => setImportModalVsb(false)}
              onOk={(e) => {
                e.stopPropagation();
                importScanDirHandle({ scandirs: importModalData });
              }}
            >
              <ul className={style.pathContent}>
                {
                  isArray(importModalData) && importModalData.map((item: any, index: number) => (
                    <li key={`index-${index}`}>
                      <span title={item.dir_path}>{item.dir_path}</span>
                      <span>{PATH_TYPES[item.path_type] || item.path_type}</span>
                      <span>{SCAN_TYPES[item.scan_type] || item.scan_type}</span>
                    </li>
                  ))
                }
              </ul>
              <p>共：{importModalData.length}条路径</p>
            </Modal>
          </div>
        )}
      </div>
      <AddModal
        isEditModal={false}
        visible={visible}
        onHide={() => setVisible(false)}
        onUpdateScanDir={onAdd}
      />
      {tab === 'sys' ? (
        <SysList
          orgSid={orgSid}
          teamName={teamName}
          repoId={repoId}
          schemeId={schemeId}
          data={sysList}
          getListData={getSysList}
        />
      ) : (
          <List
            orgSid={orgSid}
            teamName={teamName}
            repoId={repoId}
            schemeId={schemeId}
            data={cusList}
            pager={pager}
            getListData={getListData}
          />
      )}
    </div>
  );
};

export default Path;
