// Copyright (c) 2021-2023 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 过滤配置-入口文件
 */
import React, { Component } from 'react';

import { Collapse, message } from 'coding-oa-uikit';
import CaretRight from 'coding-oa-uikit/lib/icon/CaretRight';
import CaretDown from 'coding-oa-uikit/lib/icon/CaretDown';

import {
  getSchemeBasic,
  updateSchemeBasic,
  getScanDir,
} from '@src/services/schemes';

import { DEFAULT_PAGER } from '@src/constant';

import Branch from './branch';
import Path from './path';

import style from './style.scss';

const { Panel } = Collapse;

const initModalData = {
  scan_type: 2,
  path_type: 2,
};

interface IProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  schemeId: number;
}

interface IState {
  pager: any;
  scanDirsData: any;
  modalVsb: boolean; // 模态框是否显示
  modalData: any; // 模态框数据
  isEditModal: boolean; // 模态框是否是编辑状态，true-编辑，false-新增
  modalLoading: boolean; // 模态框确认按钮的加载状态
  data: any; // 分支过滤数据
  activeKeys: any; // 展开面板的key
}

class PathFilter extends Component<IProps, IState> {
  constructor(props: any) {
    super(props);
    this.state = {
      pager: DEFAULT_PAGER,
      scanDirsData: [],
      modalVsb: false,
      modalData: initModalData,
      isEditModal: true,
      modalLoading: false,
      data: {},
      activeKeys: ['path', 'issue'],
    };
  }

  public componentDidMount() {
    this.getData();
    this.getListData();
  }

  public componentDidUpdate(prevProps: IProps) {
    if (prevProps.schemeId !== this.props.schemeId) {
      this.getData();
      this.getListData();
    }
  }

  public getData = () => {
    const { repoId, schemeId, orgSid, teamName } = this.props;

    schemeId && getSchemeBasic(orgSid, teamName, repoId, schemeId).then((response) => {
      this.setState({ data: response });
    });
  };


  public getListData = (offset = DEFAULT_PAGER.pageStart, limit = DEFAULT_PAGER.pageSize) => {
    const { orgSid, teamName, repoId, schemeId } = this.props;

    schemeId && getScanDir(orgSid, teamName, repoId, schemeId, { limit, offset }).then((response) => {
      this.setState({
        pager: {
          pageSize: limit,
          pageStart: offset,
          count: response.count,
        },
        scanDirsData: response.results,
      });
    });
  };

  public onHideModal = () => {
    this.setState({
      modalVsb: false,
      modalData: initModalData,
      modalLoading: false,
    });
  };

  public onAddModal = (e: any) => {
    e?.stopPropagation();

    this.setState({
      modalVsb: true,
      isEditModal: false,
    });
  };

  public onEditModal = (data: object) => {
    this.setState({
      isEditModal: true,
      modalVsb: true,
      modalData: data,
      modalLoading: false,
    });
  };


  public updateData = (filed: string, value: any) => {
    const { data } = this.state;
    const { orgSid, teamName, repoId, schemeId } = this.props;

    updateSchemeBasic(orgSid, teamName, repoId, schemeId, {
      ...data,
      [filed]: value,
    }).then((response) => {
      message.success('更新成功');
      this.setState({ data: response });
    });
  };

  render() {
    const { data, activeKeys } = this.state;

    const { repoId, schemeId, orgSid, teamName } = this.props;

    return (
      <Collapse
        bordered={false}
        activeKey={activeKeys}
        className={style.pathFilter}
        onChange={activeKeys => this.setState({ activeKeys })}
        expandIcon={({ isActive }) => (isActive ? <CaretDown /> : <CaretRight />)}
      >
        <Panel header="路径过滤" key="path" className={style.panel}>
          <Path orgSid={orgSid} teamName={teamName} repoId={repoId} schemeId={schemeId} />
        </Panel>
        {/* <Panel
          header="路径过滤"
          key="path"
          className={style.panel}
          extra={
            activeKeys.includes('path') && (
              <PathOperation
                data={scanDirsData}
                onAddModal={this.onAddModal}
                exportScanDir={this.exportScanDir}
                importScanDir={this.importScanDir}
                onDelAll={this.onDelAllScanDir}
              />
            )
          }
        >
          <List
            data={scanDirsData}
            pager={pager}
            onDel={this.onDelScanDir}
            onEditModal={this.onEditModal}
            getListData={this.getListData}
          />

          <UpdateModal
            modalVsb={modalVsb}
            data={modalData}
            isEditModal={isEditModal}
            onHideModal={this.onHideModal}
            onUpdateScanDir={this.handleUpdateScanDir}
          />
        </Panel> */}
        <Panel header="问题过滤" key="issue" className={style.panel}>
          <Branch data={data} updateData={this.updateData} />
        </Panel>
      </Collapse>
    );
  }
}

export default PathFilter;
