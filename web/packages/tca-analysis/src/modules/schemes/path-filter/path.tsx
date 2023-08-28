// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState, useEffect } from 'react';
import { isEmpty, pick } from 'lodash';
import { saveAs } from 'file-saver';

import { message, Radio } from 'tdesign-react';

import {
  getScanDir,
  addScanDir,
  delAllScanDir,
  importScanDir,
  getSysPath,
  delSysPath,
  addSysPath,
  updateScanDir,
  delScanDir,
} from '@src/services/schemes';
import PathFilterList from '@src/components/schemes/path-filter-list';
import UpdateModal from '@src/components/schemes/path-filter-list/update-modal';
import PathOperation from '@src/components/schemes/path-filter-list/path-operation';

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
  const [editData, setEditData] = useState<any>({});

  const [visible, setVisible] = useState(false);

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
  const importScanDirHandle = (dirs: object, cb: any) => {
    importScanDir(orgSid, teamName, repoId, schemeId, dirs).then((response: any) => {
      message.success(`${response.detail || '导入成功'}`);
      getListData(initialPager.pageStart, pageSize);
      cb(false);
    });
  };

  /**
   * 编辑/添加过滤路径
   */
  const handleUpdateScanDir = (data: any) => {
    const promise = !isEmpty(editData)
      ? updateScanDir(orgSid, teamName, repoId, schemeId, editData.id, data)
      : addScanDir(orgSid, teamName, repoId, schemeId, data);

    promise
      .then(() => {
        message.success(`${!isEmpty(editData) ? '编辑' : '添加'}成功，若需将改动同步到对应的分析方案请点击同步按钮`, 5000);
        setVisible(false);
        getListData(pageStart, pageSize);
      });
  };

  /**
   * 删除路径配置
   */
  const onDelScanDir = (id: any) => {
    delScanDir(orgSid, teamName, repoId, schemeId, id).then(() => {
      message.success('删除成功');
      getListData(pageStart, pageSize);
    });
  };

  /**
   * 清空过滤路径
   */
  const onDelAll = () => {
    delAllScanDir(orgSid, teamName, repoId, schemeId).then(() => {
      message.success('清空成功');
      getListData(initialPager.pageStart, pageSize);
    });
  };

  const editSysPath = (checked: boolean, id: number) => {
    const promise = checked
      ? delSysPath(orgSid, teamName, repoId, schemeId, id)
      : addSysPath(orgSid, teamName, repoId, schemeId, id);
    promise.then(() => {
      message.success(`${checked ? '开启' : '关闭'}成功`);
      getListData();
    });
  };

  const onEditModal = (data: object) => {
    setVisible(true);
    setEditData(data);
  };


  return (
    <div className={style.path}>
      <div className={style.header}>
        <Radio.Group variant="default-filled" defaultValue='cus' onChange={(value: string) => setTab(value)}>
          <Radio.Button value='cus'>自定义</Radio.Button>
          <Radio.Button value='sys'>系统默认</Radio.Button>
        </Radio.Group>
        {tab === 'cus' && (
          <PathOperation
            onAddModal={() => {
              setEditData({});
              setVisible(true);
            }}
            exportScanDir={exportScanDir}
            importScanDir={importScanDirHandle}
            onDelAll={onDelAll}
          />
        )}
      </div>
      <UpdateModal
        visible={visible}
        onHideModal={() => setVisible(false)}
        onUpdateScanDir={handleUpdateScanDir}
        data={editData}
      />
      {tab === 'sys' ? (
        <PathFilterList
          data={sysList}
          isSysPath
          onEditSysPath={editSysPath}
        />
      ) : (
        <PathFilterList
          data={cusList}
          pager={pager}
          onDel={onDelScanDir}
          onGetScanDirs={getListData}
          onEditModal={onEditModal}
        />
      )}
    </div>
  );
};

export default Path;
