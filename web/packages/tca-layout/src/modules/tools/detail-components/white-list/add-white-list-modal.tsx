import React, { useState, useEffect } from 'react';
import { t } from '@src/utils/i18n';
import { Input, Modal, Table, message } from 'coding-oa-uikit';

import { DEFAULT_PAGER } from '@src/constant';
import { getTeams } from '@src/services/team';
import { addToolWhiteList } from '@src/services/tools';

import style from '../style.scss';

const { Column } = Table;

interface AddPackagesModalProps {
  orgSid: string;
  toolId: number;
  visible: boolean;
  whiteList: Array<any>;
  onHide: () => void;
  callback?: () => void;
}

const AddWhiteListModal = (props: AddPackagesModalProps) => {
  const { orgSid, toolId, visible, whiteList, onHide, callback } = props;
  const [list, setList] = useState([]);
  const [searchName, setSearchName] = useState('');
  const [pager, setPager] = useState(DEFAULT_PAGER);
  const { count, pageSize, pageStart } = pager;

  const [selectedRowKeys, setSelectedRowKeys] = useState<any>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (visible) {
      getListData();
    }
  }, [visible]);

  const getListData = (
    offset = pageStart,
    limit = pageSize,
    params = {
      name: searchName,
    },
  ) => {
    setLoading(true);
    getTeams({
      offset,
      limit,
      ...params,
    }).then((response: any) => {
      setPager({
        pageSize: limit,
        pageStart: offset,
        count: response.count,
      });
      setList(response.results || []);
    })
      .finally(() => {
        setLoading(false);
      });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  const addPackages = () => {
    addToolWhiteList(orgSid, toolId, selectedRowKeys).then(() => {
      message.success(t('添加成功'));
      callback?.();
      onCancel();
    });
  };

  const onCancel = () => {
    onHide();
    setSearchName('');
    setSelectedRowKeys([]);
  };

  return (
    <Modal
      title={t('添加白名单')}
      visible={visible}
      onCancel={onCancel}
      onOk={addPackages}
      className={style.antModalAddPkg}
      width={600}
    >
      <div style={{ marginBottom: 10 }}>
        <Input.Search
          allowClear
          style={{ width: 200, marginRight: 10 }}
          size='middle'
          placeholder={t('团队名称')}
          value={searchName}
          onChange={(e: any) => setSearchName(e.target.value)}
          onSearch={(value: string) => {
            getListData(0, pageSize, { name: value });
          }}
        />
      </div>
      <Table
        dataSource={list}
        rowKey={(item: any) => item.org_sid}
        loading={loading}
        size='small'
        rowSelection={{
          selectedRowKeys: selectedRowKeys.concat(whiteList),
          onChange: setSelectedRowKeys,
          getCheckboxProps: (item: any) => ({
            disabled: whiteList.includes(item.org_sid),
          }),
        }}
        pagination={{
          current: Math.floor(pageStart / pageSize) + 1,
          total: count,
          pageSize,
          showSizeChanger: true,
          showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
          onChange: onChangePageSize,
        }}
      >
        <Column
          title={t('团队名称')}
          dataIndex='name'
          key='name'
        />
      </Table>
    </Modal>
  );
};

export default AddWhiteListModal;
