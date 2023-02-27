// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState } from 'react';
import { isEmpty, isArray } from 'lodash';

import { Modal, Menu, Dropdown, Tooltip, Upload } from 'coding-oa-uikit';
import Plus from 'coding-oa-uikit/lib/icon/Plus';
import EllipsisH from 'coding-oa-uikit/lib/icon/EllipsisH';

import { SCAN_TYPES, PATH_TYPES } from '../../schemes/constants';

import style from './style.scss';

interface IProps {
  data: any[]; // 列表数据
  onAddModal: (e: any) => void;
  onDelAll: () => void;
  exportScanDir: () => void;
  importScanDir: (params: object, cb: any) => void;
}

const PathExtra = (props: IProps) => {
  const { data, onAddModal, exportScanDir, importScanDir, onDelAll } = props;
  const [importModalVsb, onChangeModalStatus] = useState(false);
  const [importModalData, onChangeImportModalData] = useState([]);

  const handleUpload = (file: any) => {
    if (file) {
      const reader = new FileReader();
      reader.readAsText(file, 'UTF-8');
      reader.onload = function () {
        onChangeModalStatus(true);
        if (this.result) {
          onChangeImportModalData(JSON.parse(this.result as string));
        }
      };
    }
    return false;
  };

  const delAll = () => {
    Modal.confirm({
      title: '清空配置',
      content: '确定清空该分析方案的所有过滤路径配置？',
      onOk: () => {
        onDelAll();
      },
    });
  };

  return (
    <div className={style.operation}>
      <a className={style.btn} onClick={onAddModal} ><Plus /> 添加过滤路径</a>
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
                  getPopupContainer={() => document.body}
                  overlayClassName={style.importTooltip}
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
              !isEmpty(data) && ([
                <Menu.Item key='export' onClick={exportScanDir}>导出路径配置</Menu.Item>,
                <Menu.Item
                  key='delAll'
                  onClick={delAll}
                  className={style.delAll}
                >一键清空路径配置</Menu.Item>,
              ])
            }
          </Menu>
        }>
        <EllipsisH onClick={(e: any) => e.stopPropagation()} />
      </Dropdown>
      <Modal
        visible={importModalVsb}
        title='批量添加过滤路径'
        className={style.importModal}
        onCancel={() => onChangeModalStatus(false)}
        onOk={(e) => {
          e.stopPropagation();
          importScanDir({ scandirs: importModalData }, onChangeModalStatus);
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
  );
};

export default PathExtra;
