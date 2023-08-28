// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState } from 'react';
import { get } from 'lodash';

import { Dialog, DialogPlugin, Dropdown, Tooltip, Upload, Button, Space } from 'tdesign-react';
import { AddIcon, EllipsisIcon } from 'tdesign-icons-react';

import { SCAN_TYPES, PATH_TYPES } from '@src/constant';

import style from './style.scss';

interface IProps {
  onAddModal: (e: any) => void;
  onDelAll: () => void;
  exportScanDir: () => void;
  importScanDir: (params: object, cb: any) => void;
}

const PathExtra = (props: IProps) => {
  const { onAddModal, exportScanDir, importScanDir, onDelAll } = props;
  const [importModalVsb, onChangeModalStatus] = useState(false);
  const [importModalData, onChangeImportModalData] = useState([]);

  const handleUpload = (file: any) => {
    if (file) {
      const reader = new FileReader();
      reader.readAsText(file.raw, 'UTF-8');
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
    const confirmDialog = DialogPlugin.confirm({
      header: '清空配置',
      body: '确定清空该分析方案的所有过滤路径配置？',
      onConfirm: () => {
        onDelAll();
        confirmDialog.hide();
      },
      onClose: () => {
        confirmDialog.hide();
      },
    });
  };

  const options = [
    {
      value: 1,
      content: (<Upload beforeUpload={handleUpload} files={[]}>
        <Tooltip
          placement="left"
          attach={() => document.body}
          overlayClassName={style.importTooltip}
          content={
            <span>
              配置提示：
              <br />
              参数：dir_path表示路径；
              <br />
              path_type表示路径类型，1为通配符，2为正则表达式；
              <br />
              scan_type表示过滤类型，1为只分析，2为只屏蔽；
              <br />[{'{"dir_path": "xxx", "path_type": 1, "scan_type": 1}'},…]
            </span>
          }
        >
          <div className={style.importButton}>导入路径配置</div>
        </Tooltip>
      </Upload>),
    },
    {
      value: 2,
      content: <div onClick={(e: any) => {
        e?.stopPropagation();
        exportScanDir();
      }}>导出路径配置</div>,
    },
    {
      value: 3,
      content: <div style={{ color: 'red' }} onClick={(e: any) => {
        e?.stopPropagation();
        delAll();
      }}>一键清空路径配置</div>,
    },
  ];

  return (
    <div className={style.operation}>
      <Space size='small'>
        <Button variant='outline' icon={<AddIcon />} onClick={onAddModal}>
          添加过滤路径
        </Button>
        <Dropdown
          placement="bottom-right"
          options={options}
          maxColumnWidth={200}
          popupProps={{
            destroyOnClose: false,
          }}
        >
          <Button variant='outline' icon={<EllipsisIcon />} onClick={(e: any) => e.stopPropagation()} />
        </Dropdown>
      </Space>
      <Dialog
        visible={importModalVsb}
        header="批量添加过滤路径"
        className={style.importModal}
        onCancel={() => onChangeModalStatus(false)}
        onConfirm={({ e }: any) => {
          e?.stopPropagation();
          importScanDir({ scandirs: importModalData }, onChangeModalStatus);
        }}
      >
        <ul className={style.pathContent}>
          {importModalData.map((item: any, index: number) => (
            <li key={`index-${index}`}>
              <span title={item.dir_path}>{item.dir_path}</span>
              <span>{get(PATH_TYPES, item.path_type, item.path_type)}</span>
              <span>{get(SCAN_TYPES, item.scan_type, item.scan_type)}</span>
            </li>
          ))}
        </ul>
        <p>共 {importModalData.length} 条路径</p>
      </Dialog>
    </div>
  );
};

export default PathExtra;
