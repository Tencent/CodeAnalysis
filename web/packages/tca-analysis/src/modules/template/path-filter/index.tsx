/**
 * 过滤配置-入口文件
 */
import React, { Component } from 'react';
import { pick, get } from 'lodash';
import { saveAs } from 'file-saver';

import { Collapse, message, Modal, Button } from 'coding-oa-uikit';
import CaretRight from 'coding-oa-uikit/lib/icon/CaretRight';
import CaretDown from 'coding-oa-uikit/lib/icon/CaretDown';

import {
  getTmplInfo,
  updateTmpl,
  delAllTmplScanDir,
  addTmplScanDir,
  updateTmplScanDir,
  delTmplScanDir,
  getTmplScanDir,
  importTmplScanDir,
  syncScheme,
} from '@src/services/template';

import { DEFAULT_PAGER } from '@src/common/constants';

import List from './list';
import PathOperation from './path-operation';
import UpdateModal from './modal';
import Branch from './branch';
import SyncModal from '../sync-modal';

import style from './style.scss';

const { Panel } = Collapse;

const initModalData = {
  scan_type: 2,
  path_type: 2,
};

interface IProps {
  orgSid: string;
  tmplId: number;
  isSysTmpl: boolean;
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
  syncModalVsb: boolean;
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
      syncModalVsb: false,
    };
  }

  public componentDidMount() {
    this.getData();
    this.getScanDirData();
  }

  public componentDidUpdate(prevProps: IProps) {
    if (prevProps.tmplId !== this.props.tmplId) {
      this.getData();
      this.getScanDirData();
    }
  }

  public getData = () => {
    const { tmplId, orgSid } = this.props;

    getTmplInfo(orgSid, tmplId).then((response) => {
      this.setState({ data: response });
    });
  };

  public getScanDirData = (limit = DEFAULT_PAGER.pageSize, offset = DEFAULT_PAGER.pageStart) => {
    const { orgSid, tmplId } = this.props;

    getTmplScanDir(orgSid, tmplId, { limit, offset }).then((response) => {
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

  /**
     * 编辑/添加过滤路径
     */
  public handleUpdateScanDir = (data: any) => {
    const { modalData, isEditModal } = this.state;
    const { orgSid, tmplId } = this.props;
    this.setState({ modalLoading: true });

    const promise = isEditModal
      ? updateTmplScanDir(orgSid, tmplId, modalData.id, data)
      : addTmplScanDir(orgSid, tmplId, data);

    promise
      .then(() => {
        message.success(`${isEditModal ? '编辑' : '添加'}成功，若需将改动同步到对应的分析方案请点击同步按钮`, 5);
        this.setState({
          modalLoading: false,
        });
        this.onHideModal();
        this.getScanDirData();
      })
      .then(() => {
        this.setState({
          modalLoading: false,
        });
      });
  };

  /**
     * 删除路径配置
     */
  public onDelScanDir = (id: any) => {
    const { orgSid, tmplId } = this.props;

    Modal.confirm({
      title: '确认删除过滤配置？',
      onOk: () => {
        delTmplScanDir(orgSid, tmplId, id).then(() => {
          message.success('删除成功');
          this.getScanDirData();
        });
      },
    });
  };

  /**
     * 一键清空路径配置
     */
  public onDelAllScanDir = () => {
    const { orgSid, tmplId } = this.props;

    delAllTmplScanDir(orgSid, tmplId).then(() => {
      message.success('已清空过滤路径');
      this.getScanDirData();
    });
  };

  /**
     * 导出路径配置
     */
  public exportScanDir = () => {
    const { orgSid, tmplId } = this.props;
    const { pager } = this.state;
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
  public importScanDir = (dirs: object, cb: any) => {
    const { orgSid, tmplId } = this.props;
    importTmplScanDir(orgSid, tmplId, dirs).then((response: any) => {
      message.success(`${response.detail || '导入成功'}`);
      cb(false);
      this.getScanDirData();
    });
  };

  public updateData = (filed: string, value: any) => {
    const { data } = this.state;
    const { tmplId, orgSid } = this.props;

    updateTmpl(orgSid, tmplId, {
      ...data,
      [filed]: value,
    }).then((response) => {
      message.success('更新成功，若需将改动同步到对应的分析方案请点击同步按钮', 5);
      this.setState({ data: response });
    });
  };

  onSync = (keys: any) => {
    const { orgSid, tmplId } = this.props;
    if (keys.length > 0) {
      syncScheme(orgSid, tmplId, {
        sync_filter_path_conf: true,
        sync_filter_other_conf: true,
        schemes: keys,
      }).then(() => {
        message.success('同步成功');
        this.setState({ syncModalVsb: false });
      });
    } else {
      message.warning('请选择需要同步的分析方案');
    }
  };

  public render() {
    const {
      pager,
      scanDirsData,
      modalVsb,
      modalData,
      isEditModal,
      data,
      activeKeys,
      syncModalVsb,
    } = this.state;

    const { tmplId, isSysTmpl } = this.props;

    return (
      <>
        <Collapse
          bordered={false}
          activeKey={activeKeys}
          className={style.pathFilter}
          onChange={activeKeys => this.setState({ activeKeys })}
          expandIcon={({ isActive }) => (isActive ? <CaretDown /> : <CaretRight />)}
        >
          <Panel
            header="路径过滤"
            key="path"
            className={style.panel}
            extra={
              activeKeys.includes('path') && !isSysTmpl && (
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
              onGetScanDirs={this.getScanDirData}
            />

            <UpdateModal
              modalVsb={modalVsb}
              data={modalData}
              isEditModal={isEditModal}
              onHideModal={this.onHideModal}
              onUpdateScanDir={this.handleUpdateScanDir}
            />
          </Panel>
          <Panel header="问题过滤" key="issue" className={style.panel}>
            <Branch isSysTmpl={isSysTmpl} data={data} updateData={this.updateData} />
          </Panel>
        </Collapse>
        {
          !isSysTmpl && (
            <>
              <Button
                type='primary'
                onClick={() => this.setState({ syncModalVsb: true })}
              >同步</Button>
              <SyncModal
                onlySync
                tmplId={tmplId}
                visible={syncModalVsb}
                onClose={() => this.setState({ syncModalVsb: false })}
                onOk={this.onSync}
              />
            </>
          )
        }
      </>
    );
  }
}

export default PathFilter;
