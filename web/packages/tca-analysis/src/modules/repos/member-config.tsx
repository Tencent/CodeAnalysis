/**
 * 项目成员设置
 */
import React, { useEffect, useState } from 'react';
import { uniqBy } from 'lodash';
import { Modal, Select, message, Button, Tag } from 'coding-oa-uikit';

import { getRepoMembers, postRepoMembers, delRepoMembers } from '@src/services/repos';
import { getProjectMembers } from '@src/utils';

import style from './style.module.scss';


interface MemberConfigProps {
  teamName: string;
  visible: boolean;
  orgSid: string;
  repoId: number;
  onCancel: (refresh?: boolean) => void;
}

const MemberConfig = (props: MemberConfigProps) => {
  const { orgSid, teamName, repoId, visible, onCancel } = props;
  const projectMembers = getProjectMembers();
  const [selectMembers, setSelectMembers] = useState([]);
  const [members, setMembers] = useState([]);

  useEffect(() => {
    if (visible) {
      getMembers();
    }
  }, [visible, repoId]);

  const getMembers = () => {
    getRepoMembers(orgSid, teamName, repoId).then((res) => {
      const { admins = [], users = [] } = res;
      const arrs = uniqBy([...admins, ...users], 'username');
      setMembers(arrs);
    });
  };

  const onAdd = () => {
    if (selectMembers?.length > 0) {
      postRepoMembers(orgSid, teamName, repoId, {
        role: 1,
        users: selectMembers,
      }).then(() => {
        message.success('仓库成员配置成功');
        getMembers();
        setSelectMembers([]);
      });
    } else {
      message.warning('请选择成员');
    }
  };

  const onDel = (user: any) => {
    Modal.confirm({
      title: `确认删除成员【${user.nickname}】？`,
      onOk() {
        delRepoMembers(orgSid, teamName, repoId, user.username).then(() => {
          message.success('删除成功');
          getMembers();
        });
      },
    });
  };

  const onReset = () => {
    onCancel();
    setSelectMembers([]);
    setMembers([]);
  };


  return (
    <Modal
      title="仓库成员设置"
      visible={visible}
      onCancel={onReset}
      afterClose={() => {
        setSelectMembers([]);
      }}
      footer={null}
      className={style.memberConfigModal}
    >
      {
        members?.length > 0 && (
          <label className={style.label}>仓库成员：</label>
        )
      }
      {
        members.map(item => (
          <Tag
            key={item.username}
            closable
            style={{ marginBottom: '10px' }}
            onClose={(e: any) => {
              e.preventDefault();
              onDel(item);
            }}
          >{item.nickname}</Tag>
        ))
      }
      <div className={style.addMembers}>
        <Select
          className={style.selectMembers}
          placeholder='选择成员'
          mode='multiple'
          value={selectMembers}
          onChange={(values: any) => setSelectMembers(values)}
        >
          {
            projectMembers.map(item => (
              <Select.Option key={item.username} value={item.username}>{item.nickname}</Select.Option>
            ))
          }
        </Select>
        <Button type='primary' onClick={onAdd}>确认添加</Button>
      </div>
    </Modal>
  );
};

export default MemberConfig;
