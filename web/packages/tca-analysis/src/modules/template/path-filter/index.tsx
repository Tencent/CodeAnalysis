// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 过滤配置-入口文件
 */
import React, { useState, useEffect } from 'react';
import { pick, get, isEmpty } from 'lodash';
import { saveAs } from 'file-saver';

import { Collapse, DialogPlugin, message } from 'tdesign-react';

import {
  getTmplInfo,
  updateTmpl,
  delAllTmplScanDir,
  addTmplScanDir,
  updateTmplScanDir,
  delTmplScanDir,
  getTmplScanDir,
  importTmplScanDir,
} from '@src/services/template';

import { DEFAULT_PAGER } from '@src/constant';

import Branch from '@src/components/schemes/path-filter-list/branch';
import PathFilterList from '@src/components/schemes/path-filter-list';
import UpdateModal from '@src/components/schemes/path-filter-list/update-modal';
import PathOperation from '@src/components/schemes/path-filter-list/path-operation';

import style from './style.scss';

const { Panel } = Collapse;

interface PathFilterProps {
  orgSid: string;
  tmplId: number;
  isSysTmpl: boolean;
}

const PathFilter = ({ orgSid, tmplId, isSysTmpl }: PathFilterProps) => {
  const [pager, setPager] = useState<any>(DEFAULT_PAGER);
  const [scanDirsData, setScanDirsData] = useState<Array<any>>([]);
  const [modalVsb, setModalVsb] = useState<boolean>(false);
  const [modalData, setModalData] = useState<any>({});
  const [data, setData] = useState<any>({});
  const [activeKeys, setActiveKeys] = useState<Array<string>>(['path', 'issue']);

  useEffect(() => {
    getTmplInfo(orgSid, tmplId).then((response) => {
      setData(response);
    });
    getTmplScanDir(orgSid, tmplId).then((response) => {
      setScanDirsData(response.results);
    });
  }, [orgSid, tmplId]);

  const getScanDirData = (offset = DEFAULT_PAGER.pageStart, limit = DEFAULT_PAGER.pageSize) => {
    getTmplScanDir(orgSid, tmplId, { limit, offset }).then((response) => {
      setPager({
        pageSize: limit,
        pageStart: offset,
        count: response.count,
      });
      setScanDirsData(response.results);
    });
  };

  const onHideModal = () => {
    setModalVsb(false);
    setModalData({});
  };

  const onAddModal = (e: any) => {
    e?.stopPropagation();
    setModalVsb(true);
    setModalData({});
  };

  const onEditModal = (data: object) => {
    setModalVsb(true);
    setModalData(data);
  };

  /**
   * 编辑/添加过滤路径
   */
  const handleUpdateScanDir = (data: any) => {
    const promise = !isEmpty(modalData)
      ? updateTmplScanDir(orgSid, tmplId, modalData.id, data)
      : addTmplScanDir(orgSid, tmplId, data);

    promise
      .then(() => {
        message.success(`${!isEmpty(modalData) ? '编辑' : '添加'}成功，若需将改动同步到对应的分析方案请点击同步按钮`, 5000);
        onHideModal();
        getScanDirData();
      });
  };

  /**
   * 删除路径配置
   */
  const onDelScanDir = (id: any) => {
    const confirmDialog = DialogPlugin.confirm({
      header: '确认删除过滤配置？',
      onConfirm: () => {
        delTmplScanDir(orgSid, tmplId, id).then(() => {
          message.success('删除成功');
          getScanDirData();
          confirmDialog.hide();
        });
      },
      onClose: () => {
        confirmDialog.hide();
      },
    });
  };

  /**
   * 一键清空路径配置
   */
  const onDelAllScanDir = () => {
    delAllTmplScanDir(orgSid, tmplId).then(() => {
      message.success('已清空过滤路径');
      getScanDirData();
    });
  };

  /**
   * 导出路径配置
   */
  const exportScanDir = () => {
    getTmplScanDir(orgSid, tmplId, { limit: pager.count }).then((response: any) => {
      const res = get(response, 'results', []).map((item: object) => pick(item, ['dir_path', 'path_type', 'scan_type']));
      const blob = new Blob([JSON.stringify(res)], { type: 'text/plain;charset=utf-8' });
      saveAs(blob, 'path_confs.json');
      message.success('导出成功');
    });
  };

  /**
   * 批量导入路径配置
   */
  const importScanDir = (dirs: object, cb: any) => {
    importTmplScanDir(orgSid, tmplId, dirs).then((response: any) => {
      message.success(`${response.detail || '导入成功'}`);
      cb(false);
      getScanDirData();
    });
  };

  const updateData = (filed: string, value: any) => {
    updateTmpl(orgSid, tmplId, {
      ...data,
      [filed]: value,
    }).then((response) => {
      message.success('更新成功，若需将改动同步到对应的分析方案请点击同步按钮', 5000);
      setData(response);
    });
  };

  return (
    <>
      <Collapse
        borderless
        value={activeKeys}
        className={style.pathFilter}
        onChange={(keys: any) => setActiveKeys(keys)}
      >
        <Panel
          header="路径过滤"
          value="path"
          className={style.panel}
          headerRightContent={
            activeKeys.includes('path') && !isSysTmpl && (
              <PathOperation
                onAddModal={onAddModal}
                exportScanDir={exportScanDir}
                importScanDir={importScanDir}
                onDelAll={onDelAllScanDir}
              />
            )
          }
        >
          <PathFilterList
            data={scanDirsData}
            pager={pager}
            onDel={onDelScanDir}
            onEditModal={onEditModal}
            onGetScanDirs={getScanDirData}
          />

          <UpdateModal
            visible={modalVsb}
            data={modalData}
            onHideModal={onHideModal}
            onUpdateScanDir={handleUpdateScanDir}
          />
        </Panel>
        <Panel header="问题过滤" value="issue" className={style.panel}>
          <Branch isSysTmpl={isSysTmpl} data={data} updateData={updateData} />
        </Panel>
      </Collapse>
    </>
  );
};

export default PathFilter;
