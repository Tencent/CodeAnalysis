import React, { useState, useEffect } from 'react';
import { t } from '@src/utils/i18n';
import { get } from 'lodash';
import { Table, Button } from 'tdesign-react';

import OrgInfo from '@plat/modules/components/org-info';
import { getOrgs } from '@src/services/orgs';
import TagType from '@src/modules/components/node-tag/tag-type';

// 模块内
import TagModal from './tag-modal';

interface TagTableProps {
  tags: any[];
  reload: () => void
}

const TagTable = ({ tags: listData, reload }: TagTableProps) => {
  const [visible, setVisible] = useState(false);
  const [selectTag, setSelectTag] = useState(null);
  const [orgList, setOrgList] = useState<Array<any>>([]);

  useEffect(() => {
    // 获取活跃团队
    getOrgs({ limit: 1000, offset: 0 }).then((res: any) => {
      setOrgList(res?.results || []);
    });
  }, []);

  const onCreateOrUpdateHandle = (tag: any = null) => {
    setVisible(true);
    setSelectTag(tag);
  };

  const columns = [
    {
      colKey: 'name',
      title: t('标签名称'),
      width: 200,
      cell: ({ row }: any) => (
        <>
          {get(row, 'display_name') || get(row, 'name')}
          <div className="text-grey-6 fs-12 mt-xs">
            {get(row, 'name')}
          </div>
        </>
      ),
    },
    {
      colKey: 'organization',
      title: t('所属团队'),
      width: 120,
      cell: ({ row }: any) => <OrgInfo org={get(row, 'org_info')} />,
    },
    {
      colKey: 'desc',
      title: t('描述'),
      width: 200,
      cell: ({ row }: any) => get(row, 'desc') || '- -',
    },
    {
      colKey: 'tag_type',
      title: t('类型'),
      width: 150,
      cell: ({ row }: any) => <TagType tag_type={get(row, 'tag_type')} />,
    },
    {
      colKey: 'op',
      title: t('操作'),
      width: 100,
      cell: ({ row }: any) => (
        <a
          onClick={() => onCreateOrUpdateHandle(row)}
        >
          {t('编辑')}
        </a>
      ),
    },
  ];

  return (
    <>
      <TagModal
        visible={visible}
        onCancel={() => setVisible(false)}
        onOk={() => {
          reload();
          setVisible(false);
        }}
        tagInfo={selectTag}
        orgList={orgList}
      />
      <div className="py-sm px-lg">
        <Button onClick={() => onCreateOrUpdateHandle()} theme="primary">
          {t('添加标签')}
        </Button>
      </div>
      <div className="px-lg">
        <Table
          rowKey='id'
          data={listData}
          columns={columns}
        />
      </div>
    </>
  );
};

export default TagTable;
