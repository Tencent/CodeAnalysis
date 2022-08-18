import React, { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Table, Button, Tag } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
import { getTags } from '@src/services/nodes';

// 模块内
import { TAG_TYPE_ENUM, TAG_TYPE_CHOICES, TAG_TYPE_COLOR } from './constants';
import TagModal from './tag-modal';
import { filter } from 'lodash';

const { Column } = Table;

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
}

const TagTable = () => {
  const [listData, setListData] = useState<Array<any>>([]);
  const [visible, setVisible] = useState(false);
  const [selectTag, setSelectTag] = useState(null);
  const { orgSid }: any = useParams();
  const orgTagList = useMemo(() => filter(listData, (tag: any) => (tag.org_sid === orgSid)), [listData]);

  /**
   * 获取标签列表
   */
  const getListData = () => {
    getTags(orgSid).then((response) => {
      setListData(response.results || []);
    });
  };

  useEffect(() => {
    getListData();
  }, []);

  const onCreateOrUpdateHandle = (tag: any = null) => {
    setVisible(true);
    setSelectTag(tag);
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
          getListData();
          setVisible(false);
        }}
        taginfo={selectTag}
      />
      <Table rowKey={(item: any) => item.id} dataSource={orgTagList}>
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
