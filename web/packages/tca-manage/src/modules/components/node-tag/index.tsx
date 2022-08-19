/**
 * 节点标签组件
 */
import React from 'react';
import { Tag } from 'tdesign-react';

import { TAG_TYPE_ENUM } from './constant';
import s from './style.scss';

interface NodeTagProps {
  /** 节点标签信息 */
  tag: any
}

/** 节点标签组件 */
const NodeTag = ({ tag }: NodeTagProps) => {
  switch (tag?.tag_type) {
    case TAG_TYPE_ENUM.PUBLIC:
      return <Tag className={s.publicTag}>
        {tag.display_name || tag.name}
      </Tag>;
    case TAG_TYPE_ENUM.PRIVATE:
      return <Tag className={s.privateTag}>
        {tag.display_name || tag.name}
      </Tag>;
    case TAG_TYPE_ENUM.DISABLED:
      return <Tag>{tag.display_name || tag.name}</Tag>;
    default:
      return <Tag className={s.publicTag}>
        {tag.display_name || tag.name}
      </Tag>;
  }
};

export default NodeTag;
