/**
 * 节点标签类别组件
 */
import React from 'react';
import { Tag } from 'tdesign-react';

import { TAG_TYPE_ENUM, TAG_TYPE_CHOICES } from './constant';
import s from './style.scss';

interface TagTypeProps {
  /** 节点标签信息 */
  tag_type: number
}

/** 节点标签类别 */
const TagType = ({ tag_type }: TagTypeProps) => {
  switch (tag_type) {
    case TAG_TYPE_ENUM.PUBLIC:
      return <Tag className={s.publicTag}>
        {TAG_TYPE_CHOICES[TAG_TYPE_ENUM.PUBLIC]}
      </Tag>;
    case TAG_TYPE_ENUM.PRIVATE:
      return <Tag className={s.privateTag}>
        {TAG_TYPE_CHOICES[TAG_TYPE_ENUM.PRIVATE]}
      </Tag>;
    case TAG_TYPE_ENUM.DISABLED:
      return <Tag>{TAG_TYPE_CHOICES[TAG_TYPE_ENUM.DISABLED]}</Tag>;
    default:
      return <Tag className={s.publicTag}>
        {TAG_TYPE_CHOICES[TAG_TYPE_ENUM.PUBLIC]}
      </Tag>;
  }
};

export default TagType;
