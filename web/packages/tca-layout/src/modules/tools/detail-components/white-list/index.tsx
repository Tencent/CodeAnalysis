/**
 * 工具白名单列表
 */
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Table, Input, Button, Tooltip, Modal, message } from 'coding-oa-uikit';
import Trash from 'coding-oa-uikit/lib/icon/Trash';

import { getToolWhiteList, delToolWhiteList } from '@src/services/tools';

import AddWhiteListModal from './add-white-list-modal';
import style from '../style.scss';

const { Column } = Table;

interface RulesProps {
  orgSid: string;
  toolId: number;
  toolDetail: any;
  tab: string;
}

const WhiteList = ({ orgSid, toolId, tab }: RulesProps) => {
  const { t } = useTranslation();
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [orgName, setOrgName] = useState('');
  const [list, setList] = useState([]);

  useEffect(() => {
    if (tab === 'whitelist') {
      getListData();
    }
  }, [orgSid, toolId, tab]);

  const getListData = () => {
    setLoading(true);
    getToolWhiteList(orgSid, toolId)
      .then((response: any) => {
        setList(response);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const onDel = (data: any) => {
    Modal.confirm({
      title: t(`确定移除白名单【 ${data?.organization?.name} 】？`),
      okButtonProps: { danger: true },
      okText: t('确定删除'),
      onOk: () => {
        delToolWhiteList(orgSid, toolId, data.id).then(() => {
          message.success(t('删除成功'));
          getListData();
        });
      },
    });
  };

  return (
    <>
      <div
        className={style.filter}
        style={{ padding: '9px 30px' }}
      >
        <Input
          placeholder={t('团队名称')}
          size='middle'
          style={{ width: 200 }}
          onChange={(e: any) => setOrgName(e.target.value)}
          value={orgName}
        />
        <Button
          type='primary'
          onClick={() => setVisible(true)}
        >
          {t('添加白名单')}
        </Button>
      </div>
      <Table
        dataSource={list.filter((item: any) => item?.organization?.name?.includes(orgName))}
        loading={loading}
        pagination={false}
        style={{ padding: '0 20px' }}
        rowKey='id'
      >
        <Column
          title={t('团队唯一标识')}
          dataIndex={['organization', 'org_sid']}
        />
        <Column
          title={t('团队名称')}
          dataIndex={['organization', 'name']}
        />
        <Column
          title={t('操作')}
          dataIndex={['organization', 'org_sid']}
          render={(orgSid: string, data: any) => (
            <Tooltip title={t('删除')}>
              <Button
                type='text'
                icon={<Trash />}
                onClick={() => onDel(data)}
              />
            </Tooltip>
          )}
        />
      </Table>
      <AddWhiteListModal
        orgSid={orgSid}
        toolId={toolId}
        visible={visible}
        whiteList={list.map((item: any) => item.organization.org_sid)}
        onHide={() => setVisible(false)}
        callback={getListData}
      />
    </>
  );
};

export default WhiteList;
