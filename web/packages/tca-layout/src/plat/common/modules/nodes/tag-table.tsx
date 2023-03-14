import React, { useState } from 'react';
import { t } from '@src/utils/i18n';
import { Table, Button, Tag } from 'coding-oa-uikit';

// 模块内
import { TAG_TYPE_ENUM, TAG_TYPE_CHOICES, TAG_TYPE_COLOR } from '@src/constant';
import TagModal from './tag-modal';

const { Column } = Table;

interface TagTableProps {
  tags: any[];
  reload: () => void
}

const TagTable = ({ tags: listData, reload }: TagTableProps) => {
  const [visible, setVisible] = useState(false);
  const [selectTag, setSelectTag] = useState(null);

  const onCreateOrUpdateHandle = (tag: any = null) => {
    setVisible(true);
    setSelectTag(tag);
  };

  const formatTypeTag = (tagType: number) => {
    switch (tagType) {
      case TAG_TYPE_ENUM.PUBLIC:
        return <Tag color={TAG_TYPE_COLOR[tagType]}>{TAG_TYPE_CHOICES[tagType]}</Tag>;
      case TAG_TYPE_ENUM.PRIVATE:
        return <Tag color={TAG_TYPE_COLOR[tagType]}>{TAG_TYPE_CHOICES[tagType]}</Tag>;
      case TAG_TYPE_ENUM.DISABLED:
        return <Tag>{TAG_TYPE_CHOICES[tagType]}</Tag>;
      default:
        return <Tag color={TAG_TYPE_COLOR[TAG_TYPE_ENUM.PUBLIC]}>{TAG_TYPE_CHOICES[TAG_TYPE_ENUM.PUBLIC]}</Tag>;
    }
  };

  return (
    <>
      <div className="py-sm">
        <Button onClick={() => onCreateOrUpdateHandle()} type="primary">
          {t('添加标签')}
        </Button>
      </div>
      <TagModal
        visible={visible}
        onCancel={() => setVisible(false)}
        onOk={() => {
          reload();
          setVisible(false);
        }}
        taginfo={selectTag}
      />
      <Table rowKey={(item: any) => item.id} dataSource={listData}>
        <Column
          title={t('标签名称')}
          dataIndex="name"
          render={(name: string, record: any) => (
            <>
            {record?.display_name || record?.name}
            <div className="text-grey-6 fs-12 mt-sm">
              {name}
            </div>
            </>
          )}
        />
        <Column
          title={t('描述')}
          dataIndex="desc"
          key="desc"
          render={(desc: string) => desc || '- -'}
        />
        <Column
          title={t('类型')}
          dataIndex="tag_type"
          key="tag_type"
          render={(type: number) => formatTypeTag(type)}
        />
        <Column
          title={t('其他操作')}
          dataIndex="op"
          render={(_: any, tag: any) => (
            <Button
              className="mr-sm"
              onClick={() => onCreateOrUpdateHandle(tag)}
            >
              {t('编辑')}
            </Button>
          )}
        />
      </Table>
    </>
  );
};

export default TagTable;
