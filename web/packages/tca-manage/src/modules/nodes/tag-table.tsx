import React, { useEffect, useState } from 'react';
// import { Link } from 'react-router-dom';
import { Table, Button } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
// import EllipsisTemplate from '@src/components/ellipsis';
import { getTags } from '@src/services/nodes';

// 模块内
import TagModal from './tag-modal';

const { Column } = Table;

const TagTable = () => {
  const [listData, setListData] = useState<Array<any>>([]);
  const [visible, setVisible] = useState(false);
  const [selectTag, setSelectTag] = useState(null);
  /**
     * 根据路由参数获取团队列表
     */
  const getListData = () => {
    getTags().then((response) => {
      setListData(response.results || []);
    });
  };

  // const onDelTagClick = (tag: any) => {
  //     delTag(tag.id).then(() => {
  //         getListData();
  //     });
  // };

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
      <Table rowKey={(item: any) => item.id} dataSource={listData}>
        <Column title={t('标签名称')} dataIndex="name" />
        <Column
          title={t('描述')}
          dataIndex="desc"
          key="desc"
          render={(desc: string) => desc || '- -'}
        />
        <Column
          title={t('是否公用')}
          dataIndex="public"
          key="public"
          render={(field: boolean) => (field ? '是' : '否')}
        />
        <Column
          title={t('其他操作')}
          dataIndex="op"
          render={(_: any, tag: any) => (
            <>
              <Button
                className="mr-sm"
                onClick={() => onCreateOrUpdateHandle(tag)}
              >
                {t('编辑')}
              </Button>
              {/* <Button danger onClick={() => onDelTagClick(tag)}>
                                    {t('删除')}
                                </Button> */}
            </>
          )}
        />
      </Table>
    </>
  );
};

export default TagTable;
